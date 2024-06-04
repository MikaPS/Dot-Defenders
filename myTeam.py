from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
from pacai.core.directions import Directions
# from pacai.student.myTeam import DummyAgent

def createTeam(firstIndex, secondIndex, isRed,
        first = 'pacai.student.myTeam.DummyAgent',
        second = 'pacai.student.myTeam.DummyAgent'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    firstAgent = DummyAgent
    secondAgent = DummyAgent

    return [
        firstAgent(firstIndex),
        secondAgent(secondIndex),
    ]

class DummyAgent(CaptureAgent):
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
            else:
                self.team = 1
            # important stats for both states:
            myPos = successorState.getPosition()
            food_offense = self.getFood(gameState).asList()
            enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
            invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]            
            teamPos = [gameState.getAgentPosition(i) for i in self.getTeam(gameState)]
            # teammates shouldn't be near each other on the y value:
            teamDistY = abs(teamPos[0][1] - teamPos[1][1])
            nextTeamPos = [successor.getAgentPosition(i) for i in self.getTeam(successor)]
            nextTeamDistY = abs(nextTeamPos[0][1] - nextTeamPos[1][1])
            nextTeamDistX = abs(nextTeamPos[0][0] - nextTeamPos[1][0])
            heightBoard = 30
            if self.team == 0 and teamDistY <= nextTeamDistY and nextTeamDistY<heightBoard/10 and nextTeamDistX<5 and nextTeamDistX>=1:
                score += 10

            # be on offense if both enemies are ghosts
            if (len(invaders) == 0):
                self.team = 0
            else:
                self.team = 1
            # want to have more food on our side of the board
            food_defense = self.getFoodYouAreDefending(gameState).asList()
            score += 10 * len(food_defense)
            if len(food_defense) <= len(food_offense) + 5:
                score -= 1000 * (len(invaders))
            # want to be close to invaders to eat them
            if (len(invaders) > 0):
                # be on offense if no invaders
                if not myState.isScared():
                    dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                    for i in self.getTeam(gameState):
                        if i != self.index:
                            teammatDists = [self.getMazeDistance(gameState.getAgentPosition(i), a.getPosition()) for a in invaders]
                    # if closer to enemey than your teammate, get the invader
                    if min(dists) < min(teammatDists):
                        self.team = 1
                        # ate a pacman
                        if min(dists) == 0:
                            score += 5000
                        elif min(dists) <= 4:
                            score += 3000
                        score += 100 / (min(dists) + 1)
                else:
                    self.team = 0
            # if in offensive state
            if self.team == 0:
                # we want to have less food to eat:
                num_food = len(food_offense)
                score -= (num_food * 2)
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
                        # eating a scared ghost is good
                        if ghost_dist == 0:
                            score += 200
                        # making sure you can reach the ghost based on their timer
                        if ghost_dist < ghost.getScaredTimer():
                            score += 1 / (ghost_dist + 1)
                    # BRAVE GHOSTS
                    else:
                        # lose conditions again
                        if ghost_dist == 0:
                            score -= 9000
                        # if brave ghost is really close, reduce score
                        if ghost_dist <= 1:
                            score -= 7000
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