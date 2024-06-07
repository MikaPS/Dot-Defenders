from pacai.agents.capture.reflex import ReflexCaptureAgent
from pacai.core.directions import Directions

def createTeam(firstIndex, secondIndex, isRed,
        first = '',
        second = ''):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    return [
        DummyOffenseAgent(firstIndex),
       DummyDefenseAgent(secondIndex)
    ]


class DummyDefenseAgent(ReflexCaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.

        IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
        """

        super().registerInitialState(gameState)

        # Your initialization code goes here, if you need any.

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        best_action = None
        best_score = float("-inf")

        for action in actions:
            score = 0
            score = self.defense(gameState, action, score)
         
            # Avoid stopping or reversing
            if action == Directions.STOP:
                score -= 100
            rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
            if action == rev:
                score -= 2

            # Update the best action
            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def defense(self, gameState, action, score):
        # important states
        successor = gameState.generateSuccessor(self.index, action)
        successorState = successor.getAgentState(self.index)
        
        myPos = successorState.getPosition()
        food_defense = self.getFoodYouAreDefending(gameState).asList()
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        
        # make sure that the defense stays as a ghost rather than a pacman
        # deafult position in the middle of the screen
        if not successorState.isPacman():
            score += 100000
        # want to have more food on our side
        # and don't want to have invaders
        score += 100 * len(food_defense)
        score -= 100 * len(invaders)
        # if we have invaders, eat them
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            if min(dists) == 0:
                score += 5000
            elif min(dists) <= 3:
                score += 3000
            score += 1000 / (min(dists) + 1)
        # if we have no invaders, stay close to the enemy
        else:
            if not successorState.isPacman():
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in enemies]
                score += 1000 / (min(dists) + 1)
        return score


class DummyOffenseAgent(ReflexCaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.

        IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
        """

        super().registerInitialState(gameState)

        # Your initialization code goes here, if you need any.

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        best_action = None
        best_score = float("-inf")

        for action in actions:
            score = 0
            score = self.offense(gameState, action, score)

            # Avoid stopping or reversing
            if action == Directions.STOP:
                score -= 100
            rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
            if action == rev:
                score -= 2

            # Update the best action
            if score > best_score:
                best_score = score
                best_action = action

        return best_action
    
    def offense(self, gameState, action, score):
        # important states
        successor = gameState.generateSuccessor(self.index, action)
        successorState = successor.getAgentState(self.index)
        
        myPos = successorState.getPosition()
        food_offense = self.getFood(gameState).asList()
        ghosts = [a for a in gameState.getAgentStates() if not a.isPacman()]
        
        # want to have less food on the enemy side
        num_food = len(food_offense)
        score -= 5 * num_food
        food_dists = [self.getMazeDistance(myPos, food) for food in food_offense]
        # go to closet food
        if food_dists:
            score += 100 / (min(food_dists) + 1)
        
        # ghost behavior:
        for ghost in ghosts:
            ghost_dist = self.getMazeDistance(myPos, ghost.getPosition())
            # eat scared ghosts when possible
            if ghost.isScared():
                if ghost_dist == 0:
                    score += 200
                if ghost_dist < ghost.getScaredTimer():
                    score += 1 / (ghost_dist + 1)
            # run away from brave ghosts
            else:
                if ghost_dist == 0:
                    score -= 9000
                if ghost_dist <= 1:
                    score -= 7000
        
        return score

# --- our previous iteration of the code
class DummyAgent(ReflexCaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.

        IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
        """

        super().registerInitialState(gameState)

        # Your initialization code goes here, if you need any.
        self.features = {}
        # Computes whether we're on defense (1) or offense (0).
        self.team = 1  # 1 = defense, 0 = offense

    def chooseAction(self, gameState):
        """
        Randomly pick an action.
        """
        actions = gameState.getLegalActions(self.index)
        
        best_action = None
        best_score = float("-inf")
        # go through all the actions
        for action in actions:
            score = 0
            # get the successor based on the action
            myState = gameState.getAgentState(self.index)
            successor = gameState.generateSuccessor(self.index, action)
            successorState = successor.getAgentState(self.index)
            # check if we're offense (agent is pacman) or defense (it's a ghost)
            if (myState.isPacman()):
                self.team = 0

            # important stats for both states:
            myPos = successorState.getPosition()
            food_offense = self.getFood(gameState).asList()
            enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
            # want to have more food on our side of the board
            food_defense = self.getFoodYouAreDefending(gameState).asList()
            score += 10 * len(food_defense)
            if len(food_defense) <= len(food_offense) + 5:
                enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
                invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
                score -= 1000 * (len(invaders))
                # want to be close to invaders to eat them
                if (len(invaders) > 0):
                    if not myState.isScared():
                        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                        # ate a pacman
                        if min(dists) == 0:
                            score += 5000
                        elif min(dists) <= 3:
                            score += 3000
                        score += 100 / (min(dists) + 1)
            # if in offensive state
            if self.team == 0:
                # print("in offesnse!")
                # we want to have less food to eat:
                num_food = len(food_offense)
                score -= (num_food * 5)
                # find the closest food
                food_dists = []
                for food in food_offense:
                    food_dist = self.getMazeDistance(myPos, food)
                    score += 1 / (food_dist + 1)
                    food_dists.append(food_dist)
                score += 1 / (min(food_dists) + 1)
                # find dist to all ghosts, and check if they're scared or not
                g = []
                numScared = 0
                ghosts = [a for a in enemies if not a.isPacman() and a.getPosition() is not None]
                for ghost in ghosts:
                    ghostPosition = ghost.getPosition()
                    ghost_dist = self.getMazeDistance(myPos, ghostPosition)
                    g.append(ghost_dist)
                    # SCARED GHOSTS
                    if ghost.isScared():
                        numScared += 1
                        # eating a scared ghost is really good
                        if ghost_dist == 0:
                            score += 500
                        if ghost_dist <= 1 and ghost.getScaredTimer() > 1:
                            score += 200
                        # making sure you can reach the ghost based on their timer
                        if ghost_dist < ghost.getScaredTimer():
                            score += 10 / (ghost_dist + 1)
                    # BRAVE GHOSTS
                    else:
                        # lose conditions again
                        if ghost_dist == 0:
                            score -= 7000
                        # if brave ghost is really close, reduce score
                        if ghost_dist <= 1:
                            score -= 5000
                # want to have lots of scared ghosts
                if numScared > 0:
                    score += 500
                # print("current score is: ", score)
            # defense
            else:
                # want to have less invaders
                enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
                invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
                score -= 1000 * (len(invaders))
                # want to be close to invaders to eat them
                if (len(invaders) > 0):
                    dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                    # ate a pacman
                    if min(dists) == 0:
                        score += 5000
                    elif min(dists) <= 5:
                        score += 3000
                    score += 100 / (min(dists) + 1)
            
            # relvant to both states:
            # don't want the agent to not move or go back and forth
            if (action == Directions.STOP):
                score -= 100
            rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
            if (action == rev):
                score -= 2
            # update best action
            if score >= best_score:
                best_score = score
                best_action = action

        return best_action  # random.choice(actions)
            # don't want the agent to not move or go back and forth
            if (action == Directions.STOP):
                score -= 100
            rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
            if (action == rev):
                score -= 2
            # update best action
            if score >= best_score:
                best_score = score
                best_action = action

        return best_action  # random.choice(actions)