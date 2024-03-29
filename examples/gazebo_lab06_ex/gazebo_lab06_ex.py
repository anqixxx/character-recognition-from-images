#!/usr/bin/env python3
import gym
from gym import wrappers
import gym_gazebo
import time
import numpy
import random
import time

import qlearn
import liveplot

from matplotlib import pyplot as plt


def render():
    render_skip = 0  # Skip first X episodes.
    render_interval = 50  # Show render Every Y episodes.
    render_episodes = 10  # Show Z episodes every rendering.

    if (x % render_interval == 0) and (x != 0) and (x > render_skip):
        env.render()
    elif (((x-render_episodes) % render_interval == 0) and (x != 0) and
          (x > render_skip) and (render_episodes < x)):
        env.render(close=True)


if __name__ == '__main__':

    env = gym.make('Gazebo_Lab06-v0')

    outdir = '/tmp/gazebo_gym_experiments'
    env = gym.wrappers.Monitor(env, outdir, force=True)
    plotter = liveplot.LivePlot(outdir)

    last_time_steps = numpy.ndarray(0)

    # Decreased episilon so model can learn
    qlearn = qlearn.QLearn(actions=range(env.action_space.n),
                           alpha=0.2, gamma=0.8, epsilon=0.7)
    

    # qlearn.loadQ("QValues_A+.pickle")

    initial_epsilon = qlearn.epsilon

    epsilon_discount = 0.998

    start_time = time.time()
    total_episodes = 10_000
    highest_reward = 0

    for x in range(total_episodes):
        done = False

        cumulated_reward = 0  # Should going forward give more reward then L/R?

        if qlearn.epsilon > 0.05:
            qlearn.epsilon *= epsilon_discount

        # render() #defined above, not env.render()
        observation = env.reset()
        state = ''.join(map(str, observation))

        i = -1
        while True:
            i += 1

            # Pick an action based on the current state
            action = qlearn.chooseAction(state)
            # Execute the action and get feedback
            observation, reward, done, info = env.step(action)
            cumulated_reward += reward

            nextState = ''.join(map(str, observation))

            qlearn.learn(state, action, reward, nextState)

            env._flush(force=True)

            if not(done):
                state = nextState
            else:
                last_time_steps = numpy.append(last_time_steps, [int(i + 1)])
                break

        print("===== Completed episode {}".format(x))

        if highest_reward < cumulated_reward:
            highest_reward = cumulated_reward
            qlearn.saveQ("QValues_A+")


        if (x > 0) and (x % 5 == 0):
            qlearn.saveQ("QValues")
            plotter.plot(env)

        m, s = divmod(int(time.time() - start_time), 60)
        h, m = divmod(m, 60)
        print ("Starting EP: " + str(x+1) +
               " - [alpha: " + str(round(qlearn.alpha, 2)) +
               " - gamma: " + str(round(qlearn.gamma, 2)) +
               " - epsilon: " + str(round(qlearn.epsilon, 2)) +
               "] - Reward: " + str(cumulated_reward) +
               "     Time: %d:%02d:%02d" % (h, m, s))

    # Github table content
    print ("\n|"+str(total_episodes)+"|"+str(qlearn.alpha)+"|" +
           str(qlearn.gamma)+"|"+str(initial_epsilon)+"*" +
           str(epsilon_discount)+"|"+str(highest_reward) + "| PICTURE |")

    l = last_time_steps.tolist()
    l.sort()

    print("Parameters: a="+str)
    print("Overall score: {:0.2f}".format(last_time_steps.mean()))
    print("Best 100 score: {:0.2f}".
          format(reduce(lambda x, y: x + y, l[-100:]) / len(l[-100:])))

    env.close()
