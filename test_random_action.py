from random_actions import RandomActions
actions = RandomActions(600)

actions.randomize_action()
csv = actions.generate_csv("actions.csv")
print(csv)

actions.voice_action(100)