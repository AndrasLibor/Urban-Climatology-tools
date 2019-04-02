import sys
import gdal
import ogr
import osr
import math
import json
import datetime


def heightWidthCalc(geoJSON, rastArray, thresholdVal, pts, xPos, yPos, colsNum, rowsNum, pixelWidth, pixelHeight, xLeft, xRight, yTop, yBottom, noData):

    # calculating direction perpendicular to the line based on the line coordinates
    # gradually increasing distance and checking if threshold value is reached, then measuring distance and height difference from central pixel
    # then doing the same thing in the opposite direction, also measuring distance and height if threshold is reached
    # calculates mean of the 2 height values and sum of the 2 width (distance) values, then calculating H/W value
    # appending crucial value to the GeoJSON dictionary - location, height, width and H/W values


    if pts[0][0] == pts[1][0]:

        horStep = 0
        vertStep = 1

    elif pts[1][0] == pts[1][1]:

        horStep = 1
        vertStep = 0


    else:

        slope = ((pts[1][1] - pts[0][1]) / (pts[1][0] - pts[0][0]))

        slopeInDeg = abs(math.degrees(math.atan(slope)))

        if (pts[1][0] > pts[0][0] and pts[1][1] > pts[0][1]) or (
                pts[1][0] < pts[0][0] and pts[1][1] < pts[0][1]):

            if slopeInDeg > 45:

                horStep = 1
                vertStep = 1.0 / slope

            elif slopeInDeg < 45:

                horStep = slope
                vertStep = 1

            else:

                horStep = 1
                vertStep = 1

        elif (pts[1][0] > pts[0][0] and pts[1][1] < pts[0][1]) or (
                pts[1][0] < pts[0][0] and pts[1][1] > pts[0][1]):

            if slopeInDeg > 45:

                horStep = 1
                vertStep = -1.0 / slope

            elif slopeInDeg < 45:

                horStep = slope
                vertStep = -1

            else:

                horStep = 1
                vertStep = -1



    heightA = 0
    heightB = 0
    distanceA = 0
    distanceB = 0


    if abs(horStep) > abs(vertStep):

        horCount = 0
        verCount = 0
        smallStep = 0
        iterCount = 0



        while iterCount < 500:

            iterCount += 1

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

            iterCount += 1

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

            iterCount += 1

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

            iterCount += 1

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

            iterCount += 1

            if yPos + iterCount >= rowsNum or yPos + iterCount < 0 or xPos + iterCount >= colsNum or xPos + iterCount < 0:

                xDist = abs(iterCount - 1 * horStep * pixelWidth)
                yDist = abs(iterCount - 1 * vertStep * pixelHeight)

                distanceA = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                heightA = 0

                break

            elif rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] == noData:

                continue

            elif rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] - rastArray[yPos][xPos] > thresholdVal:

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

            iterCount += 1

            if yPos + iterCount >= rowsNum or yPos + iterCount < 0 or xPos + iterCount >= colsNum or xPos + iterCount < 0:

                xDist = abs(iterCount - 1 * horStep * pixelWidth)
                yDist = abs(iterCount - 1 * vertStep * pixelHeight)

                distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                heightB = 0

                break

            elif rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] == noData:

                continue

            elif rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] - rastArray[yPos][xPos] > thresholdVal:

                xDist = abs(iterCount * horStep * pixelWidth)
                yDist = abs(iterCount * vertStep * pixelHeight)

                distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                heightB = rastArray[yPos + (vertStep * iterCount)][xPos + (horStep * iterCount)] - rastArray[yPos][xPos]

                break

            elif iterCount == 500:

                xDist = abs(iterCount * horStep * pixelWidth)
                yDist = abs(iterCount * vertStep * pixelHeight)

                distanceB = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))
                heightB = 0

                break


    if distanceA != 0 and distanceB != 0:

        thresholdVal = float(thresholdVal)
        distanceA = float(distanceA)
        distanceB = float(distanceB)
        heightA = float(heightA)
        heightB = float(heightB)


        x = (xLeft + xRight) / 2.0
        y = (yTop + yBottom) / 2.0
        heightMean = (heightA + heightB) / 2.0
        totalWidth = distanceA + distanceB
        hwRatio = heightMean / totalWidth


        dict = {"type": "Feature",
                "properties": {"Threshold": thresholdVal,
                               "CanWidthA": distanceA,
                               "CanWidthB": distanceB,
                               "CanWidthTotal": totalWidth,
                               "CanHeightA": heightA,
                               "CanHeightB": heightB,
                               "CanHeightMean": heightMean,
                               "HWRatio": hwRatio
                               },
                "geometry": {"type": "Point",
                             "coordinates": [x, y]
                             }
                }

        geoJSON["features"].append(dict)

        print "GeoJSON appended"


def canyonCalc(rasterPath, vectorPath, thresholdVal, frame, outputDir, outputName):

    # printing current time to make it easier to estimate the whole process time
    print datetime.datetime.now()

    # opening raster and vector data
    lineData = ogr.Open(vectorPath)
    rasterData = gdal.Open(rasterPath, gdal.GA_ReadOnly)

    # checking projection of the raster data - EPSG code is needed for the output data
    projRast = osr.SpatialReference(wkt=rasterData.GetProjection())
    epsgRast = projRast.GetAttrValue('AUTHORITY', 1)

    # getting vector layer from vector data
    layer = lineData.GetLayer()

    # extracting important data from the raster data - pixel size, number of pixels in columns/ rows, starting location
    trans = rasterData.GetGeoTransform()

    pixelWidth = trans[1]
    pixelHeight = trans[5]
    xMin = trans[0]
    yMax = trans[3]
    colsNum = rasterData.RasterXSize
    rowsNum = rasterData.RasterYSize

    # setting output file path and name: crucial informations, like epsg code and threshold value are included
    if '.' in str(thresholdVal):

        thres = str(thresholdVal).split('.')

        file = open(outputDir + '\canyon' + outputName + 'thres' + thres[0] + '_' + thres[1] + '_' + epsgRast + '.geojson', 'w')

    else:

        thres = str(thresholdVal)

        file = open(outputDir + '\canyon' + outputName + 'Thres' + thresholdVal + '_' + epsgRast + '.geojson', 'w')


    # setting projection of the output data with EPSG code
    crsName = "urn:ogc:def:crs:EPSG::" + epsgRast

    # creating GeoJSON dictionary; later to be filled with values during calculation
    geoJSON = {
        "type": "FeatureCollection",
        "name": outputName,
        "crs": {"type": "name", "properties": {"name": crsName}},
        "features": []}

    # printing some important information for the user
    print 'Pixel width: ' + str(pixelWidth)
    print 'Pixel height: ' + str(pixelHeight)
    print 'X min: ' + str(xMin)
    print 'Y max: ' + str(yMax)
    print 'Columns: ' + str(colsNum)
    print 'Rows: ' + str(rowsNum)

    # reading in raster data as an array and getting its no data value
    rastArray = rasterData.GetRasterBand(1).ReadAsArray()
    noDataValue = rasterData.GetRasterBand(1).GetNoDataValue()

    # creating a vector geometry with the extent size of the raster data
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xMin, yMax)
    ring.AddPoint(xMin, yMax + (rowsNum * pixelHeight))
    ring.AddPoint(xMin + (colsNum * pixelWidth), yMax + (rowsNum * pixelHeight))
    ring.AddPoint(xMin + (colsNum * pixelWidth), yMax)
    ring.AddPoint(xMin, yMax)

    rastExtent = ogr.Geometry(ogr.wkbPolygon)
    rastExtent.AddGeometry(ring)

    # getting number of features (geometries) in the vector layer
    featureNum = layer.GetFeatureCount()


    # if there are multiline geometries in the layer, they are splitted
    lineSplit = ogr.Geometry(ogr.wkbMultiLineString)


    for i in range(0, featureNum):

        line = layer.GetFeature(i)
        vectGeom = line.GetGeometryRef()
        pts = vectGeom.GetPoints()

        if len(pts) == 2:

            simpleLine = ogr.Geometry(ogr.wkbLineString)
            simpleLine.AddPoint(pts[0][0], pts[0][1])
            simpleLine.AddPoint(pts[1][0], pts[1][1])

            lineSplit.AddGeometry(simpleLine)

        elif len(pts) > 2:

            for j in range(1, len(pts)):

                simpleLine = ogr.Geometry(ogr.wkbLineString)
                simpleLine.AddPoint(pts[j - 1][0], pts[j - 1][1])
                simpleLine.AddPoint(pts[j][0], pts[j][1])

                lineSplit.AddGeometry(simpleLine)



    # creating area of interrest by intersecting the vector layer with the raster extent, then counts features in the intersection
    aoi = rastExtent.Intersection(lineSplit)

    featureNum = aoi.GetGeometryCount()


    # iterating through every pixel, checking for an intersection with current line geometry
    # if an intersection is found, H/W value is calculated and GeoJSON object is appended
    # starting all over with a different line geometry
    for xPos in range(frame, colsNum - frame):



        xLeft = xMin + (xPos * pixelWidth)
        xRight = xMin + ((xPos + 1) * pixelWidth)


        print xPos

        for yPos in range(frame, rowsNum - frame):



            # if there is a noDataValue at current location, then the algorithm will ignore it
            if rastArray[yPos][xPos] == noDataValue:

                continue


            yTop = yMax + (yPos * pixelHeight)
            yBottom = yMax + ((yPos + 1) * pixelHeight)



            boundingBox = ogr.Geometry(ogr.wkbLinearRing)

            boundingBox.AddPoint(xLeft, yTop)
            boundingBox.AddPoint(xLeft, yBottom)
            boundingBox.AddPoint(xRight, yBottom)
            boundingBox.AddPoint(xRight, yTop)
            boundingBox.AddPoint(xLeft, yTop)

            rastGeom = ogr.Geometry(ogr.wkbPolygon)
            rastGeom.AddGeometry(boundingBox)


            for feature in range(0, featureNum):

                vectGeom = aoi.GetGeometryRef(feature)
                pts = vectGeom.GetPoints()



                intersection = rastGeom.Intersect(vectGeom)

                if intersection == True:

                    # the function defined above is called and used with the arguments of the current pixel and line geometry intercting the pixel
                    heightWidthCalc(geoJSON, rastArray, thresholdVal, pts, xPos, yPos, colsNum, rowsNum, pixelWidth, pixelHeight, xLeft, xRight, yTop, yBottom, noDataValue)



    # writing GeoJSON dictionary into a GeoJSON file and saves it
    json.dump(geoJSON, file)

    print 'GeoJSON dumped'

    file.close()

    print 'File closed - PROCESS FINISHED'

    print datetime.datetime.now()


def main():
    rasterPath = sys.argv[1]
    vectorPath = sys.argv[2]
    threshold = float(sys.argv[3])
    frame = int(sys.argv[4])
    outputDir = sys.argv[5]
    outputName = sys.argv[6]

    canyonCalc(rasterPath, vectorPath, threshold, frame, outputDir, outputName)


if __name__ == '__main__':
    main()