import heapq
import os
import time
from copy import deepcopy
from datetime import datetime
from pathlib import Path


def getTimestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def createHash(grid):
    gridItem = sorted(grid.items())
    return str(gridItem)

def calcManhatten(x,y):
    return abs(x[0] - y[0]) + abs(x[1] - y[1])

def calcWeights(grid):
    portWeight = 0
    shipWeight = 0

    for (row,col), (weight, desc) in grid.items():
        if col > 6:
            shipWeight += weight
        if col <= 6:
            portWeight += weight

    return portWeight, shipWeight

def isBalanced(grid, prevPort, prevShip):
    port, ship = calcWeights(grid)
    diff = abs(port - ship)
    total = prevPort + prevShip
    balanced = .10 * total

    if diff <= balanced:
        return True
    else:
        return False

def movableContainers(grid):
    tops = {}
    result = []
    for (row,col), (weight,desc) in grid.items():
        if col not in tops or row > tops[col][0]:
            tops[col] = (row, weight, desc, (row,col))

    for col, (row,weight, desc,pos) in tops.items():
        result.append((pos,weight,desc))

    return result

def canPlace(grid,col, nanSlots):
    if col < 1 or col > 12:
        return None

    occupiedRows = [row for (row,c) in grid.keys() if c == col]

    if not occupiedRows:
        if (1,col) in nanSlots:
            return None
        
        return 1

    maxRow = max(occupiedRows)

    if maxRow >= 8:
        return None
    
    nextRow = maxRow + 1

    if (nextRow, col) in nanSlots:
        return None

    return nextRow

def heuristicFunction(grid, firstPort, firstShip):
    portWeight, shipWeight = calcWeights(grid)
    diff = abs(portWeight - shipWeight)
    total = firstPort + firstShip
    balanced = .10 * total

    if diff <= balanced:
        return 0

    reduceWeight = diff - balanced
    move = reduceWeight / 2

    heavierSide = ""
    if portWeight > shipWeight:
        heavierSide = "port"
    else:
        heavierSide = "ship"
    
    movable = movableContainers(grid) 

    if heavierSide == "port":
        heavyContainers = [(pos,weight, desc) for pos, weight, desc in movable if pos[1] <= 6]
    else:
        heavyContainers = [(pos,weight,desc) for pos, weight, desc in movable if pos[1] >=7]
    
    if not heavyContainers:
        return float('inf')

    bestContainer = min(heavyContainers, key=lambda x: abs(x[1] - move))
    bestPos = bestContainer[0]

    if heavierSide == "port":
        distance = 7 - bestPos[1]
    else:
        distance = bestPos[1] - 6

    cranePos = (8, 0)
    craneTravelEstimate = calcManhatten(cranePos, bestPos)
    craneReturnEstimate = calcManhatten(bestPos, cranePos)
    totalEstimate = craneTravelEstimate + distance + craneReturnEstimate

    return max(1, totalEstimate)


def getMoves(grid,firstPort,firstShip, nanSlots):
    portWeight, shipWeight = calcWeights(grid)
    validMoves = []
    diff = abs(portWeight - shipWeight)
    total = firstPort + firstShip
    balanced = .10 * total

    if diff <= balanced:
        return validMoves 
    
    if portWeight <= shipWeight:
        moveFromCols = range(7, 13)
        moveToCols = range(1,7)
    else:
        moveFromCols = range(1,7)
        moveToCols = range(7,13)
    
    movableContainer = movableContainers(grid)

    for fromPos, weight, desc in movableContainer:
        fromRow, fromCol = fromPos
        if fromCol not in moveFromCols:
            continue

        for toCol in moveToCols:
            toRow = canPlace(grid, toCol, nanSlots)

            if toRow is None:
                continue

            toPos = (toRow,toCol)
            validMoves.append((fromPos, toPos, weight, desc))

    return validMoves

def makeMove(grid, fromPos, toPos, weight, desc, cranePos):
    newGrid = deepcopy(grid)
    del newGrid[fromPos]
    newGrid[toPos] = (weight, desc)
    
    travelToContainer = calcManhatten(cranePos, fromPos)
    moveContainer = calcManhatten(fromPos, toPos)
    cost = travelToContainer + moveContainer
    
    return newGrid, cost, toPos

def aStar(firstGrid, firstPort, firstShip, nanSlots, timeLimit = 180, log_print=print):
    counter = 0
    prioQueue = []
    closedSet = {}

    craneStart = (8, 0)

    hCost = heuristicFunction(firstGrid, firstPort, firstShip)
    fCost = 0 + hCost

    heapq.heappush(prioQueue, (fCost, counter, 0, firstGrid, [], craneStart))
    counter += 1

    nodesSeen = 0
    startTime = time.time()
    bestSol = None  
    bestImbalance = float('inf')

    while prioQueue:
        if time.time() - startTime > timeLimit:
            log_print(f"{getTimestamp()} Time limit reached")

            if bestSol:
                log_print(f"{getTimestamp()} Returning best solution so far")
                return bestSol
            
            return None
        
        fCost, x, gCost, currGrid, moves, cranePos = heapq.heappop(prioQueue)
        nodesSeen += 1

        if nodesSeen % 100 == 0:
            port, ship = calcWeights(currGrid)
            log_print(f"{getTimestamp()} Seen {nodesSeen} nodes, Imbalance: {abs(port - ship)}kg, Moves: {len(moves)}")

        if isBalanced(currGrid, firstPort, firstShip):
            log_print(f"{getTimestamp()} Solution is found in {time.time() - startTime:.2f} seconds")
            log_print(f"{getTimestamp()} Total moves: {len(moves)}")

            port, ship = calcWeights(currGrid)
            currImbalance = abs(port - ship)

            log_print(f"{getTimestamp()} Port weight: {port} kg")
            log_print(f"{getTimestamp()} Ship weight: {ship} kg")
            log_print(f"{getTimestamp()} Imbalance: {currImbalance}kg")

            return moves
        
        port, ship = calcWeights(currGrid)
        currImbalance = abs(port - ship)

        if currImbalance < bestImbalance:
            bestImbalance = currImbalance
            bestSol = moves
        
        currState = createHash(currGrid)
        
        if currState in closedSet:
            if gCost >= closedSet[currState]:
                continue
        
        closedSet[currState] = gCost
        
        validMoves = getMoves(currGrid, firstPort, firstShip, nanSlots)

        for fromPos, toPos, weight, desc in validMoves:
            newGrid, mCost, newCranePos = makeMove(currGrid, fromPos, toPos, weight, desc, cranePos)

            newG = gCost + mCost

            newState = createHash(newGrid)

            if newState in closedSet:
                if newG >= closedSet[newState]:
                    continue
            
            newH = heuristicFunction(newGrid, firstPort, firstShip)
            newF = newG + newH

            nextMove = {"from": fromPos, "to": toPos, "weight": weight, "description": desc, "cost": mCost}

            newMoves = moves + [nextMove]

            heapq.heappush(prioQueue, (newF, counter, newG, newGrid, newMoves, newCranePos))
            counter += 1

    log_print(f"{getTimestamp()} NO SOLUTION FOUND")
    return None


def parseManifest(filename):
    nanSlots = set()
    grid = {}

    fileExtension = os.path.splitext(filename)[1].lower()

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                if fileExtension == ".csv":
                    parts = line.split(',')
                    if len(parts) < 4:
                        continue

                    row = int(parts[0].strip())
                    col = int(parts[1].strip())
                    weight = int(parts[2].strip())
                    desc = ','.join(parts[3:]).strip()

                else:
                    endPos = line.index(']')
                    strPos = line[1:endPos]
                    row, col = map(int, strPos.split(','))

                    startWeight = line.index('{', endPos) + 1
                    endWeight = line.index('}', startWeight)
                    weight = int(line[startWeight:endWeight])

                    startDesc = line.index(',', endWeight) + 1
                    desc = line[startDesc:].strip()

                if desc == "NAN":
                    nanSlots.add((row,col))
                    continue

                if desc == "UNUSED":
                    continue

                grid[(row,col)] = (weight, desc)

            except (ValueError, IndexError):
                continue

    return grid, nanSlots


def generateManifest(filename, finalGrid, baseName):
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    outputDir = os.path.join(scriptDir, 'Output')

    currTime = datetime.now()
    timeStamp = currTime.strftime("%m_%d_%Y_%H%M")
    
    saveFilename = f"{baseName}_{timeStamp}OUTBOUND.txt"
    savePath = os.path.join(outputDir, saveFilename)

    with open(filename, 'r') as f:
        lines = f.readlines()

    newLines = []
    fileExtension = os.path.splitext(filename)[1].lower()

    if fileExtension == ".csv":
        for line in lines:
            line = line.strip()

            if not line:
                newLines.append('\n')
                continue
            
            try: 
                parts = line.split(',')
                row = int(parts[0].strip())
                col = int(parts[1].strip())

                if (row,col) in finalGrid:
                    weight, desc = finalGrid[(row,col)]
                    newLine = f"{row},{col},{weight},{desc}\n"
                    newLines.append(newLine)
                else:
                    if len(parts) >= 4 and parts[3].strip() == "NAN":
                        newLines.append(line + '\n')
                    else:
                        newLine = f"{row},{col},0,UNUSED\n"
                        newLines.append(newLine)

            except:
                newLines.append(line + '\n')
    
    else:
        for line in lines:
            line = line.strip()

            if not line:
                newLines.append('\n')
                continue

            try:
                endPos = line.index(']')
                strPos = line[1:endPos]
                row, col = map(int, strPos.split(','))

                if (row, col) in finalGrid:
                    weight, desc = finalGrid[(row,col)]
                    newLine = f"[{row:02d},{col:02d}], {{{weight:05d}}}, {desc}\n"
                    newLines.append(newLine)
                else:
                    if "NAN" in line:
                        newLines.append(line + '\n')
                    else:
                        newLine = f"[{row:02d},{col:02d}], {{00000}}, UNUSED\n"
                        newLines.append(newLine)

            except:
                newLines.append(line + '\n')

    with open(savePath, 'w') as f:
        f.writelines(newLines)
    
    return savePath


def displayGrid(grid, nanSlots, gridName="Grid", log_print=print):
    log_print(f"{getTimestamp()} {gridName}:")
    
    for row in range(8, 0, -1):
        line = "["
        for col in range(1, 13):
            if (row, col) in grid:
                weight, desc = grid[(row, col)]
                line += f"{weight:4}"
            elif (row, col) in nanSlots:
                line += f"{-1:4}"
            else:
                line += f"{0:4}"
            
            if col < 12:
                line += " "
        line += "]"
        log_print(line)

def main():
    manifest = input("Enter the manifest filename (e.g., ShipCase5.csv): ").strip()
    now = datetime.now()
    timestamp = now.strftime("%m_%d_%Y_%H%M")
    log_filename = f"KeoghsPort{timestamp}_{manifest[:-4]}.txt"
    
    # create folder if it no exist
    output_dir = Path("Output")
    output_dir.mkdir(exist_ok=True)
    log_file = output_dir / log_filename

    if not os.path.dirname(manifest):
        manifest = os.path.join('..', 'Dataset', manifest)
    
    if not os.path.exists(manifest):
        print(f"Error: File '{manifest}' not found.")
        return
    
    baseName = os.path.splitext(os.path.basename(manifest))[0]

    with open(log_file,"w") as f:
        def log_print(*args, **kwargs):
            # Add timestamp to each log entry
            #timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = " ".join(str(arg) for arg in args)
            log_entry = f"{msg}"
            print(*args, **kwargs)
            f.write(log_entry + "\n")
            f.flush()

        def log_hide(*args, **kwargs):
            # Add timestamp to each log entry
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = " ".join(str(arg) for arg in args)
            log_entry = f"[{timestamp_str}] {msg}"
            f.write(log_entry + "\n")
            f.flush()
            
        log_print(f"{getTimestamp()} Program starts.")
        
        grid, nanSlots = parseManifest(manifest)
        
        numContainers = len(grid)
        log_print(f"{getTimestamp()} File open, this is {baseName}. There are total of {numContainers} containers on the ship.")
        
        port, ship = calcWeights(grid)
        
        if numContainers == 0:
            log_print(f"{getTimestamp()} Ship is empty - already balanced!")
            savePath = generateManifest(manifest, grid, baseName)
            log_print(f"{getTimestamp()} File was written to Output directory.")
            log_print(f"{getTimestamp()} Program ends. Computation time: 0 minutes")
            return
        
        if numContainers == 1:
            log_print(f"{getTimestamp()} Ship has one container - already balanced!")
            savePath = generateManifest(manifest, grid, baseName)
            log_print(f"{getTimestamp()} File was written to Output directory.")
            log_print(f"{getTimestamp()} Program ends. Computation time: 0 minutes")
            return
        
        if isBalanced(grid, port, ship):
            log_print(f"{getTimestamp()} Ship is already balanced!")
            savePath = generateManifest(manifest, grid, baseName)
            log_print(f"{getTimestamp()} File was written to Output directory.")
            log_print(f"{getTimestamp()} Program ends. Computation time: 0 minutes")
            return
        
        startTime = time.time()
        solution = aStar(grid, port, ship, nanSlots, timeLimit=180, log_print=log_print)
        
        if solution is None:
            log_print(f"{getTimestamp()} Failed to find solution!")
            savePath = generateManifest(manifest, grid, baseName)
            return
        
        for i, move in enumerate(solution, 1):
            fromRow, fromCol = move['from']
            toRow, toCol = move['to']
            cost = move['cost']
            log_print(f"{getTimestamp()} Move {i}: [{fromRow}, {fromCol}] -> [{toRow}, {toCol}], Steps(minutes): {cost}")
        
            if i < len(solution) + 1:
                input(f"{getTimestamp()} Press ENTER to move onto next step")
                log_hide(f"{getTimestamp()} Press ENTER to move onto next step")

        totalCost = sum(move['cost'] for move in solution)
        log_print(f"{getTimestamp()} Finished a cycle. Total steps: {totalCost}")
        
        finalGrid = deepcopy(grid)
        for move in solution:
            del finalGrid[move['from']]
            finalGrid[move['to']] = (move['weight'], move['description'])
        
        displayGrid(finalGrid, nanSlots, "Balanced Grid", log_print)

        def log_hide(*args, **kwargs):
            # Add timestamp to each log entry
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = " ".join(str(arg) for arg in args)
            log_entry = f"[{timestamp_str}] {msg}"
            f.write(log_entry + "\n")
            f.flush()

        writeComment = input(f"{getTimestamp()} Do you have any comments (y/n): ")
        log_hide(f"{getTimestamp()} Do you have any comments (y/n): {writeComment}")
        while writeComment != "n":
            comment = input(f"{getTimestamp()} Type your comment here: ")
            log_hide(f"{getTimestamp()} Comment: {comment}")
            writeComment = input(f"{getTimestamp()} Do you have any comments (y/n): ")
            log_hide(f"{getTimestamp()} Do you have any comments (y/n): {writeComment}")
        
        outboundPath = generateManifest(manifest, finalGrid, baseName)
        log_print(f"{getTimestamp()} File was written to Output directory.")
        
        # computationTime = int(time.time() - startTime)
        log_print(f"{getTimestamp()} Program ends. Computation time: {totalCost} minutes")



if __name__ == "__main__":
    main()