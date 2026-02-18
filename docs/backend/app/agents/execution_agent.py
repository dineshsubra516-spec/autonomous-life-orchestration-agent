class ExecutionAgent:
    def execute(self, food, travel):
        return {
            "food_ordered": food["item"],
            "travel_booked": travel["mode"]
        }
