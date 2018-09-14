'''
Created on Sep 12, 2018

@author: Max

Code based off of PySource's tutorial:
https://pysource.com/2018/07/19/check-if-two-images-are-equal-with-opencv-and-python/
'''
from __future__ import print_function
import cv2
import numpy as np
# import os


MAX_MATCHES = 500
GOOD_MATCH_PERCENT = 0.20

''' Read images in '''
# Read [pattern] & convert to grayscale
refFilename = "form.jpg"
imPattern = cv2.imread("../images/food1.jpg", cv2.IMREAD_COLOR)
imPatternGray = cv2.cvtColor(imPattern, cv2.COLOR_BGR2GRAY)

# Read [photo] & convert to grayscale
imFilename = "scanned-form.jpg" 
imPhoto = cv2.imread("../images/test1.jpg", cv2.IMREAD_COLOR)
imPhotoGray = cv2.cvtColor(imPhoto, cv2.COLOR_BGR2GRAY)

''' Compare features between [photo] and [pattern] '''
# Detect ORB features and compute descriptors.
orb = cv2.ORB_create(MAX_MATCHES)
kpPhoto, descPhoto = orb.detectAndCompute(imPhotoGray, None)
kpPattern, descPattern = orb.detectAndCompute(imPatternGray, None)
# Match features.
matcherAlign = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True) # cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
matchesAlign = matcherAlign.match(descPhoto, descPattern, None)
# Sort matches by score
matchesAlign.sort(key=lambda x: x.distance, reverse=False)
# Remove not so good matches
numGoodMatches = int(len(matchesAlign) * GOOD_MATCH_PERCENT)
matchesAlign = matchesAlign[:numGoodMatches]
# Draw top matches
# imMatches = cv2.drawMatches(imPhoto, kpPhoto, imPattern, kpPattern, matchesAlign, None) 
# path = '../images'
# cv2.imwrite(os.path.join(path , "matches.jpg"), imMatches)

''' Homography stuff '''
# Extract location of good matches
points1 = np.zeros((len(matchesAlign), 2), dtype=np.float32)
points2 = np.zeros((len(matchesAlign), 2), dtype=np.float32)
for i, match in enumerate(matchesAlign):
    points1[i, :] = kpPhoto[match.queryIdx].pt
    points2[i, :] = kpPattern[match.trainIdx].pt
# Find homography
h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
# Use homography
height, width, channels = imPattern.shape
imAligned = cv2.warpPerspective(imPhoto, h, (width, height))
imAligned = cv2.cvtColor(imAligned, cv2.COLOR_BGR2GRAY)
# Print estimated homography
# print("Estimated homography : \n",  h)


''' Compare features between [aligned image] and [pattern] '''
kpAligned, descAligned = orb.detectAndCompute(imAligned, None)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(descAligned, descPattern)
matches = sorted(matches, key = lambda x:x.distance)
# keep matches if their locations are close enough
good_points = []
for m in matches:
    if m.distance < 50: # idk what unit 50 is in
        good_points.append(m)

''' Define similarity index (good_points / min(# of kps 1, # of kps 2) '''
number_keypoints = 0
if len(kpAligned) <= len(kpPattern):
    number_keypoints = len(kpAligned)
else:
    number_keypoints = len(kpPattern)
similarity = len(good_points) / number_keypoints
isMatch = similarity > 0.2
 
''' Output! '''
print("Keypoints 1ST Image: " + str(len(kpAligned)))
print("Keypoints 2ND Image: " + str(len(kpPattern)))
print("GOOD Matches:", len(good_points))
print("Match Rating:", similarity)
if isMatch:
    print("Pattern Detected!")
else:
    print("Pattern Not Detected.")

# Display results
result = cv2.drawMatches(imPatternGray, kpAligned, imAligned, kpPattern, good_points, None)
cv2.imshow("result", cv2.resize(result, None, fx=0.4, fy=0.4))
# cv2.imwrite("feature_matching.jpg", result)
# cv2.imshow("imPatternGray", cv2.resize(imPatternGray, None, fx=0.4, fy=0.4))
# cv2.imshow("Duplicate", cv2.resize(imAligned, None, fx=0.4, fy=0.4))

cv2.waitKey(0)
cv2.destroyAllWindows()