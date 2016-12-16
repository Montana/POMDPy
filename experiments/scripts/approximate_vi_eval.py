from pickle_wrapper import load_pkl
from plot_alpha_vectors import plot_alpha_vectors
import os
import time
from pomdpy.agent import Results
import numpy as np


my_dir = os.path.dirname(__file__)
weight_dir = os.path.join(my_dir, '..', '..', 'experiments', 'pickle_jar')

gamma_8 = load_pkl(os.path.join(weight_dir, 'VI_planning_horizon_8.pkl'))
gamma_1 = load_pkl(os.path.join(weight_dir, 'VI_planning_horizon_1.pkl'))


def plot_baseline(horizon, baseline):
    plot_alpha_vectors('Value Iteration - Planning Horizon - {}'.format(horizon), baseline, 3)


def eval_baseline(n_epochs, agent, horizon):

    if horizon == 8:
        baseline = gamma_8
    elif horizon == 1:
        baseline = gamma_1
    else:
        raise ValueError('Unsupported baseline planning horizon')

    solver = agent.solver_factory(agent)
    model = agent.model

    experiment_results = Results()

    for epoch in range(n_epochs):
        epoch_start = time.time()

        model.reset_for_epoch()

        # evaluate agent
        reward = 0
        discounted_reward = 0
        discount = 1.0
        belief = model.get_initial_belief_state()

        while True:
            action, v_b = solver.select_action(belief, baseline)
            step_result = model.generate_step(action)

            if not step_result.is_terminal:
                belief = model.belief_update(belief, action, step_result.observation)

            reward += step_result.reward
            discounted_reward += discount * step_result.reward
            discount *= model.discount

            if step_result.is_terminal:
                break

        print('\ntotal reward: {} discounted reward: {}'.format(reward, discounted_reward))

        experiment_results.time.add(time.time() - epoch_start)
        experiment_results.undiscounted_return.count += 1
        experiment_results.undiscounted_return.add(reward)
        experiment_results.discounted_return.count += 1
        experiment_results.discounted_return.add(discounted_reward)

    print('\nepochs: ' + str(model.n_epochs))
    print('ave undiscounted return: ' + str(experiment_results.undiscounted_return.mean) +
            ' +- ' + str(experiment_results.undiscounted_return.std_err()))
    print('ave discounted return: ' + str(experiment_results.discounted_return.mean) +
            ' +- ' + str(experiment_results.discounted_return.std_err()))
    print('ave time/epoch: ' + str(experiment_results.time.mean))


def random_baseline(n_epochs, agent):
    model = agent.model

    experiment_results = Results()

    for epoch in range(n_epochs):
        epoch_start = time.time()

        model.reset_for_epoch()

        # evaluate agent
        reward = 0
        discounted_reward = 0
        discount = 1.0
        belief = model.get_initial_belief_state()

        while True:
            action = np.random.randint(model.num_actions)
            step_result = model.generate_step(action)

            if not step_result.is_terminal:
                belief = model.belief_update(belief, action, step_result.observation)

            reward += step_result.reward
            discounted_reward += discount * step_result.reward
            discount *= model.discount

            if step_result.is_terminal:
                break

        print('\ntotal reward: {} discounted reward: {}'.format(reward, discounted_reward))

        experiment_results.time.add(time.time() - epoch_start)
        experiment_results.undiscounted_return.count += 1
        experiment_results.undiscounted_return.add(reward)
        experiment_results.discounted_return.count += 1
        experiment_results.discounted_return.add(discounted_reward)

    print('\nepochs: ' + str(model.n_epochs))
    print('ave undiscounted return: ' + str(experiment_results.undiscounted_return.mean) +
          ' +- ' + str(experiment_results.undiscounted_return.std_err()))
    print('ave discounted return: ' + str(experiment_results.discounted_return.mean) +
          ' +- ' + str(experiment_results.discounted_return.std_err()))
    print('ave time/epoch: ' + str(experiment_results.time.mean))