from graphviz import Digraph

class State:
    def __init__(self, name):
        self.name = name
        self.transitions = []  # list of (target_state, action)

    def add_transition(self, target_state, action):
        for i, (state, existing_action) in enumerate(self.transitions):
            if state.name == target_state.name:  # compare by name
                if action in existing_action:
                    return
                self.transitions[i] = (state, f"{existing_action}\n{action}")
                return
        self.transitions.append((target_state, action))




class StateMachine:
    def __init__(self):
        self.states = {}

    def add_state(self, name):
        if name in self.states:
            return self.states[name]  # return existing state
        state = State(name)
        self.states[name] = state
        return state


    def export_graphviz(self, filename="state_machine", view=False):
        dot = Digraph(comment="State Machine", format="pdf")

        # Add transitions
        for state in self.states.values():
            for target, action in state.transitions:
                dot.edge(state.name, target.name, label=action)

        dot.render(filename, view=view)

if __name__ == "__main__":
    # Example usage:
    sm = StateMachine()

    idle = sm.add_state("Idle")
    processing = sm.add_state("Processing")
    success = sm.add_state("Success")
    error = sm.add_state("Error",)

    # Multiple incoming transitions
    idle.add_transition(processing, "start_processing")
    processing.add_transition(success, "complete_ok")
    processing.add_transition(success, "complete_ok2")
    processing.add_transition(error, "fail")
    idle.add_transition(success, "jump_to_success")  # second entry to same node

    # Export
    sm.export_graphviz(view=True)
