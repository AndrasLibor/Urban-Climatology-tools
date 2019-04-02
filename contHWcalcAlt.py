import sys
import gdal
import ogr
import osr
import math
import numpy as np
import datetime

def array2raster(newRasterfn, originX, originY, pixelWidth, pixelHeight, array, epsg, noData):

    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.SetNoDataValue(noData)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(epsg)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


def contHWCalc(rastArray, outArray, thresholdVal, degreeStep, noData, xPos, yPos, outX, outY, colsNum, rowsNum, pixelWidth, pixelHeight):

    # making an empty list; H/W values are going to be stored here
    pixelValHperW = []

    # checking a full circle of H/W values - after a direction is checked, the opposite direction is checked too, that's why we stop iteration at 180
    # gradually increasing distance and checking if threshold value is reached, then measuring distance and height difference from central pixel
    # then doing the same thing in the opposite direction, also measuring distance and height if threshold is reached
    # calculates mean of the 2 height values and sum of the 2 width (distance) values, then calculating H/W value and appending it to the empty list above
    # starting all over with different direction
    # when full circle is done, the mean of the H/W values are calculated and used as a value for the current cell of the array
    for deg in range(0, 180, degreeStep):


        if deg == 0:

            horStep = 0
            vertStep = -1

        elif 0 < deg < 45:

            horStep = math.tan(math.radians(deg))
            vertStep = -1

        elif deg == 45:

            horStep = 1
            vertStep = -1

        elif 45 < deg < 90:

            horStep = 1
            vertStep = -1 / math.tan(math.radians(deg))

        elif deg == 90:

            horStep = 1
            vertStep = 0

        elif 90 < deg < 135:

            horStep = 1
            vertStep = -1 / math.tan(math.radians(deg))

        elif deg == 135:

            horStep = 1
            vertStep = 1

        elif 135 < deg < 180:

            horStep = math.tan(math.radians(deg)) * -1
            vertStep = 1


        distanceA = 0
        distanceB = 0
        heightA = 0
        heightB = 0

        if abs(horStep) > abs(vertStep):

            horCount = 0
            verCount = 0
            smallStep = 0
            iterCount = 0


            while iterCount < 500:

                iterCount = iterCount + 1

                horCount = horCount + horStep
                smallStep = smallStep + vertStep

                if smallStep >= 1:

                    verCount = verCount + 1
                    smallStep = smallStep - 1

                elif smallStep <= -1:

                    verCount = verCount - 1
                    smallStep = smallStep + 1

                if yPos + verCount >= rowsNum or yPos + verCount < 0 or xPos + horCount >= colsNum or xPos + horCount < 0:

                    xDist = abs(iterCount - 1 * horStep * pixelWidth)
                    yDist = abs(iterCount - 1 * vertStep * pixelHeight)

                    distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightA = 0

                    break

                elif rastArray[yPos + verCount][xPos + horCount] == noData:

                    continue

                elif rastArray[yPos + verCount][xPos + horCount] - rastArray[yPos][xPos] > thresholdVal:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightA = rastArray[yPos + verCount][xPos + horCount] - rastArray[yPos][xPos]

                    break

                elif iterCount == 500:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightA = 0

                    break

            horStep = horStep * -1
            vertStep = vertStep * -1

            horCount = 0
            verCount = 0
            smallStep = 0
            iterCount = 0


            while iterCount < 500:

                iterCount = iterCount + 1

                horCount = horCount + horStep
                smallStep = smallStep + vertStep

                if smallStep >= 1:
                    verCount = verCount + 1
                    smallStep = smallStep - 1

                elif smallStep <= -1:

                    verCount = verCount - 1
                    smallStep = smallStep + 1

                if yPos + verCount >= rowsNum or yPos + verCount < 0 or xPos + horCount >= colsNum or xPos + horCount < 0:

                    xDist = abs(iterCount - 1 * horStep * pixelWidth)
                    yDist = abs(iterCount - 1 * vertStep * pixelHeight)

                    distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightB = 0

                    break

                elif rastArray[yPos + verCount][xPos + horCount] == noData:

                    continue

                elif rastArray[yPos + verCount][xPos + horCount] - rastArray[yPos][xPos] > thresholdVal:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightB = rastArray[yPos + verCount][xPos + horCount] - rastArray[yPos][xPos]

                    break

                elif iterCount == 500:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightB = 0

                    break




        elif abs(horStep) < abs(vertStep):

            horCount = 0
            verCount = 0
            smallStep = 0
            iterCount = 0


            while iterCount < 500:

                iterCount = iterCount + 1

                verCount = verCount + vertStep
                smallStep = smallStep + horStep

                if smallStep >= 1:

                    horCount = horCount + 1
                    smallStep = smallStep - 1


                elif smallStep <= -1:

                    horCount = horCount - 1
                    smallStep = smallStep + 1

                if yPos + verCount >= rowsNum or yPos + verCount < 0 or xPos + horCount >= colsNum or xPos + horCount < 0:

                    xDist = abs(iterCount - 1 * horStep * pixelWidth)
                    yDist = abs(iterCount - 1 * vertStep * pixelHeight)

                    distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightA = 0

                    break

                elif rastArray[yPos + verCount][xPos + horCount] == noData:

                    continue

                elif rastArray[yPos + verCount][xPos + horCount] - rastArray[yPos][xPos] > thresholdVal:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightA = rastArray[yPos + verCount][xPos + horCount] - rastArray[yPos][xPos]

                    break

                elif iterCount == 500:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightA = 0

                    break

            horStep = horStep * -1
            vertStep = vertStep * -1

            horCount = 0
            verCount = 0
            smallStep = 0
            iterCount = 0


            while iterCount < 500:

                iterCount = iterCount + 1

                verCount = verCount + vertStep
                smallStep = smallStep + horStep

                if smallStep >= 1:
                    horCount = horCount + 1
                    smallStep = smallStep - 1


                elif smallStep <= -1:

                    horCount = horCount - 1
                    smallStep = smallStep + 1

                if yPos + verCount >= rowsNum or yPos + verCount < 0 or xPos + horCount >= colsNum or xPos + horCount < 0:

                    xDist = abs(iterCount - 1 * horStep * pixelWidth)
                    yDist = abs(iterCount - 1 * vertStep * pixelHeight)

                    distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightB = 0

                    break

                elif rastArray[yPos + verCount][xPos + horCount] == noData:

                    continue

                elif rastArray[yPos + verCount][xPos + horCount] - rastArray[yPos][xPos] > thresholdVal:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightB = rastArray[yPos + verCount][xPos + horCount] - rastArray[yPos][xPos]

                    break

                elif iterCount == 500:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightB = 0

                    break



        elif abs(horStep) == abs(vertStep):

            iterCount = 0


            while iterCount < 500:

                iterCount = iterCount + 1

                if yPos + iterCount >= rowsNum or yPos + iterCount < 0 or xPos + iterCount >= colsNum or xPos + iterCount < 0:

                    xDist = abs(iterCount - 1 * horStep * pixelWidth)
                    yDist = abs(iterCount - 1 * vertStep * pixelHeight)

                    distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightA = 0

                    break

                elif rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] == noData:

                    continue

                elif rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] - \
                        rastArray[yPos][xPos] > thresholdVal:
                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightA = rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] - rastArray[yPos][xPos]

                    break

                elif iterCount == 500:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightA = 0

                    break

            horStep = horStep * -1
            vertStep = vertStep * -1

            iterCount = 0


            while iterCount < 500:

                iterCount = iterCount + 1

                if yPos + iterCount >= rowsNum or yPos + iterCount < 0 or xPos + iterCount >= colsNum or xPos + iterCount < 0:

                    xDist = abs(iterCount - 1 * horStep * pixelWidth)
                    yDist = abs(iterCount - 1 * vertStep * pixelHeight)

                    distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightB = 0

                    break

                elif rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] == noData:

                    continue

                elif rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] - \
                        rastArray[yPos][xPos] > thresholdVal:
                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightB = rastArray[yPos + (vertStep * iterCount)][ xPos + (horStep * iterCount)] - rastArray[yPos][xPos]

                    break

                elif iterCount == 500:

                    xDist = abs(iterCount * horStep * pixelWidth)
                    yDist = abs(iterCount * vertStep * pixelHeight)

                    distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                    heightB = 0

                    break

        if distanceA != 0 and distanceB != 0:

            totalWidth = distanceA + distanceB
            meanHeight = (heightA + heightB) / 2.0

            heightWidth = meanHeight / totalWidth

            pixelValHperW.append(heightWidth)

    if len(pixelValHperW) != 0:

        hwRatio = sum(pixelValHperW) / len(pixelValHperW)

        outArray[outY][outX] = hwRatio


    return outArray


def canyonCalc(rasterPath, thresholdVal, degreeStep, pixelStep, frame, outputDir, outputName):

    # printing current time to make it easier to estimate the whole process time
    print datetime.datetime.now()


    # opening the raster data and checking its projection - EPSG code to be used in setting the output data
    rasterData = gdal.Open(rasterPath, gdal.GA_ReadOnly)
    projRast = osr.SpatialReference(wkt=rasterData.GetProjection())
    epsgRast = int(projRast.GetAttrValue('AUTHORITY', 1))

    # extracting important data from the raster data - pixel size, number of pixels in columns/ rows, starting location
    trans = rasterData.GetGeoTransform()
    pixelWidth = trans[1]
    pixelHeight = trans[5]
    xMin = trans[0]
    yMax = trans[3]
    colsNum = rasterData.RasterXSize
    rowsNum = rasterData.RasterYSize

    # setting the pixel size for the output data (only important when using a pixel step greater than 1)
    outWidth = pixelWidth * pixelStep
    outHeight = pixelHeight * pixelStep

    # reading in raster data as an array and getting its no data value
    rastArray = rasterData.GetRasterBand(1).ReadAsArray()
    noDataValue = rasterData.GetRasterBand(1).GetNoDataValue()


    # making the output array filled with the noDataValue; each cell value to be calculated later on
    # array size is determined by the pixel step - output arrays axes are pixel step times smaller
    outArray = np.full((rastArray.shape[0] / pixelStep, rastArray.shape[1] / pixelStep), noDataValue)

    # if the degree step is too big, it is reduced, otherwise the result won't be accurate enough
    # decreasing degree step value (if needed), so a full circle can be inspected
    if degreeStep > 30:

        degreeStep = 15

    if 360 % degreeStep != 0:

        while 360 % degreeStep != 0:

            degreeStep = degreeStep - 1


    # setting output file path and name: crucial informations, like epsg code and threshold value are included
    thres = str(thresholdVal).split('.')

    newRastPath = outputDir + r'\canyonCont' + outputName + 'thres' + thres[0] + '_' + thres[1] + '_' + str(epsgRast) + '.tif'

    #printing some important information for the user
    print 'Pixel width: ' + str(pixelWidth)
    print 'Pixel height: ' + str(pixelHeight)
    print 'X min: ' + str(xMin)
    print 'Y max: ' + str(yMax)
    print 'Columns: ' + str(colsNum)
    print 'Rows: ' + str(rowsNum)

    # setting frame size to adapt new output array size
    # also doing this for x and y value, so the output array's values can be filled one by one, without gaps
    frame = frame - (frame % pixelStep)
    outX = frame / pixelStep
    for xPos in range(frame, colsNum - frame, pixelStep):


        print xPos

        outY = frame / pixelStep

        for yPos in range(frame, rowsNum - frame, pixelStep):

            '''
            if (xPos < 100 or xPos > colsNum - 100) and (yPos < 100 or yPos > rowsNum - 100):

                continue
            '''

            # if there is a noDataValue at current location, then the algorithm will ignore it
            if rastArray[yPos][xPos] == noDataValue:

                continue


            else:


                # this is the key part: the value for current array cell will be calculated and the array will be updated
                outArray = contHWCalc(rastArray, outArray, thresholdVal, degreeStep, noDataValue, xPos, yPos, outX, outY, colsNum, rowsNum, pixelWidth, pixelHeight)

            outY = outY + 1

        outX = outX + 1


    # creating output raster file at specified location
    array2raster(newRastPath, xMin, yMax, outWidth, outHeight, outArray, epsgRast, noDataValue)

    rasterData = None

    print datetime.datetime.now()


def main():
    rasterPath = sys.argv[1]
    threshold = float(sys.argv[2])
    deg = int(sys.argv[3])
    pix = int(sys.argv[4])
    frame = int(sys.argv[5])
    outputDir = sys.argv[6]
    outputName = sys.argv[7]

    canyonCalc(rasterPath, threshold, deg, pix, frame, outputDir, outputName)


if __name__ == '__main__':
    main()