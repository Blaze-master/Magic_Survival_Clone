import os
import numpy as np
import tensorflow as tf
from collections import deque

class DeepQModel():
    def __init__(
            self, 
            base_model, 
            optimizer,
            loss_fn, 
            action_space,
            state_decoder=None, 
            buffer_size = 3000, 
            gamma = 0.95,):
        
        self.model = base_model
        self.target = tf.keras.models.clone_model(self.model)
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.state_decoder = state_decoder
        self.action_space = action_space
        self.memory = deque(maxlen=buffer_size)
        self.gamma = gamma

    def remember(self, state, action, reward, next_state, done, truncated):
        self.memory.append((state, action, reward, next_state, done, truncated))
    
    def sample_experiences(self, batch_size):
        indices = np.random.randint(len(self.memory), size=batch_size)
        batch = [self.memory[index] for index in indices]
        return [
            np.array([experience[field_index] for experience in batch])
            for field_index in range(6)
        ] # [states, actions, rewards, next_states, dones, truncateds]

    def epsilon_greedy_policy(self, state, epsilon):
        if np.random.rand() < epsilon:
            action_index = np.random.randint(len(self.action_space)) # random action
        else:
            Q_values = self.model(state)[0]
            action_index = np.argmax(Q_values) # optimal action according to the DQN
        return action_index
    
    def play_one_step(
            self, 
            state, 
            epsilon, 
            env=None, 
            training=True):
        if self.state_decoder: state = self.state_decoder(state)
        action = self.epsilon_greedy_policy(state, epsilon)
        if env:
            next_state, reward, done, truncated = env.step(action)
            if training: self.remember(state, action, reward, self.state_decoder(next_state) if self.state_decoder else next_state, done, truncated)
            return next_state, reward, done, truncated
        else:
            return action
    
    def training_step(self, batch_size, track_loss=False):
        states, actions, rewards, next_states, dones, truncateds = self.sample_experiences(batch_size)
        runs = 1.0 - (dones | truncateds) # episode is not done or truncated

        if isinstance(states[0], dict):
            s = {key: np.array([state[key][0].tolist() for state in states]) for key in states[0]}
            ns = {key: np.array([state[key][0].tolist() for state in next_states]) for key in next_states[0]}
            states, next_states = s, ns
        
        # Double DQN
        next_Q_values = self.model.predict(next_states, verbose=0) # ≠ target.predict()
        best_next_actions = next_Q_values.argmax(axis=1)
        next_mask = tf.one_hot(best_next_actions, len(self.action_space)).numpy()
        max_next_Q_values = (self.target.predict(next_states, verbose=0) * next_mask).sum(axis=1)
                
        target_Q_values = rewards + runs * self.gamma * max_next_Q_values
        target_Q_values = target_Q_values.reshape(-1, 1)
        
        mask = tf.one_hot(actions, len(self.action_space))
        with tf.GradientTape() as tape:
            all_Q_values = self.model(states, training=True)
            Q_values = tf.reduce_sum(all_Q_values * mask, axis=1, keepdims=True)
            loss = tf.reduce_mean(self.loss_fn(target_Q_values, Q_values))
        
        grads = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))
        if track_loss:
            return loss.numpy()

    def load(self, path):
        self.model.load_weights(path)
        self.update_target()

    def save(self, path):
        self.model.save_weights(path)
    
    def update_target(self):
        self.target.set_weights(self.model.get_weights())
    

def load_model(path):
    base_model = None
    with open(os.path.join(path, "build_config.txt"), "r") as f:
        build_config = f.read()
        exec(build_config)
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
    loss_fn = tf.keras.losses.mean_squared_error
    action_space = np.array([list(map(int, list(bin(i)[2:].zfill(4)))) for i in range(16)]) # Every possible combination of directions
    state_decoder = None
    rl_model = DeepQModel(base_model, optimizer, loss_fn, action_space, state_decoder)
    rl_model.load(os.path.join(path, "weights"))
    return rl_model

# train_kwargs: current_step, current_episode, total_episodes, epsilon_threshold, min_epsilon
def get_model_action(
        model: DeepQModel,
        mode,
        state,
        **train_kwargs
    ):
    if mode == "test":
        model_action = model.play_one_step(state, epsilon=0.0, training=False)
    elif mode == "train":
        epsilon = max(train_kwargs["min_epsilon"], 1 - train_kwargs["current_episode"] / (train_kwargs["total_episodes"] * train_kwargs["epsilon_threshold"]))
        model_action = model.play_one_step(state, epsilon=epsilon)
    return model_action

def receive_response(
        model: DeepQModel,
        new_state,
        reward,
        done,
        truncated,
    ):
    model.remember(model.state_decoder(new_state) if model.state_decoder else new_state, reward, done, truncated)

# Note: Save the text in this function in a file named "build_config.txt" in the same directory as the model weights
def build_model():
    tf.random.set_seed(42)

    inputs = tf.keras.layers.Input(shape=(...)) #Expected input shape
    hidden1 = tf.keras.layers.Dense(32, activation="relu", kernel_initializer="he_normal")(inputs)
    hidden2 = tf.keras.layers.Dense(32, activation="relu", kernel_initializer="he_normal")(hidden1)

    state_values = tf.keras.layers.Dense(1)(hidden2)
    raw_advantages = tf.keras.layers.Dense(...)(hidden2) # Expected number of actions
    advantages = raw_advantages - tf.reduce_max(raw_advantages, axis=1, keepdims=True)
    Q_values = state_values + advantages

    base_model = tf.keras.Model(inputs=[inputs], outputs=[Q_values])
    #Text cut-off
    return base_model

class Trainer():
    def __init__(
            self,
            model_path: str = None,
            num_steps = None, # Number of ticks to train per episode
            batch_size = 128,
            num_episodes = 200,
            first_training_epoch = 20,
            min_epsilon = 0.01,
            epsilon_threshold = 0.8,
            update_interval = 10,
            initial_lr = 1e-3,
            final_lr = None,
    ):
        self.rl_model = None
        self.num_steps = num_steps
        self.batch_size = batch_size
        self.num_episodes = num_episodes
        self.first_training_epoch = first_training_epoch
        self.min_epsilon = min_epsilon
        self.epsilon_threshold = epsilon_threshold
        self.update_interval = update_interval
        self.initial_lr = initial_lr
        self.final_lr = final_lr
        try:
            self.rl_model = load_model(model_path)
        except FileNotFoundError:
            base_model = build_model()
            optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
            loss_fn = tf.keras.losses.mean_squared_error
            state_decoder = None
            action_space = np.array([list(map(int, list(bin(i)[2:].zfill(4)))) for i in range(16)]) # Every possible combination of directions
            self.rl_model = DeepQModel(
                base_model, 
                optimizer, 
                loss_fn, 
                action_space, 
                state_decoder)
        self.model_weights_path = os.path.join(model_path, "weights")
        self.reward_history = []
        self.survival_history = []
        self.current_episode = 0
        self.current_step = 0
        self.episode_rewards = 0
        self.lr_factor = (self.final_lr/self.initial_lr)**(1/self.num_episodes) if self.final_lr else None
    
    def get_action(self, state):
        self.current_step += 1
        epsilon = max(self.min_epsilon, 1 - self.current_episode / (self.num_episodes * self.epsilon_threshold))
        return self.rl_model.play_one_step(state, epsilon=epsilon, training=False)
    
    def receive_response(self, new_state, reward, done, truncated):
        self.rl_model.remember(self.rl_model.state_decoder(new_state) if self.rl_model.state_decoder else new_state, reward, done, truncated)
        self.episode_rewards += reward
    
    def end_episode(self):
        self.reward_history.append(self.episode_rewards)
        self.survival_history.append(self.current_step)
        self.current_episode += 1
        self.current_step = 0
        if self.current_episode >= self.first_training_epoch:
            self.rl_model.training_step(self.batch_size)
        if self.current_episode+1 % self.update_interval == 0:
            self.rl_model.update_target()
        if self.final_lr: self.rl_model.optimizer.learning_rate = self.initial_lr * (self.lr_factor**self.current_episode)
        self.rl_model.save(self.model_weights_path)
    
    def get_metrics(self):
        return self.reward_history, self.survival_history


if __name__ == "__main__": pass