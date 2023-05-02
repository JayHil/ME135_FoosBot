import cv2
import sys
import numpy as np

#Takes in images org and warp and returns warp aligned to org. org and warp are assumed to be color images.
def alignImage(org, warp):
	org = cv2.cvtColor(org, cv2.COLOR_BGR2RGB)
	warp = cv2.cvtColor(warp, cv2.COLOR_BGR2RGB)
	org_gray = cv2.cvtColor(org, cv2.COLOR_BGR2GRAY)
	warp_gray = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)

	maxFeatures = 500
	orb = cv2.ORB_create(maxFeatures)

	#detect key features and compute descriptors
	orgKey, orgDesc = orb.detectAndCompute(org_gray, None)
	warpKey, warpDesc = orb.detectAndCompute(warp_gray, None)

	descMatcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
	matches = descMatcher.match(orgDesc, warpDesc, None)

	matches = sorted(matches, key=lambda x: x.distance, reverse=False)

	matches = matches[:int(len(matches)*0.1)]

	#extract homography
	orgPts = np.zeros((len(matches), 2), dtype=np.float32)
	warpPts = np.zeros((len(matches), 2), dtype=np.float32)

	#assign points from good matches
	for i, match in enumerate(matches):
		orgPts[i, :] = orgKey[match.queryIdx].pt
		warpPts[i, :] = warpKey[match.trainIdx].pt

		h, mask = cv2.findHomography(warpPts, orgPts, 0)

		print(h)

		#warp the image and return the frame
		height, width = org_gray.shape
		warp_reg = cv2.warpPerspective(warp, h, (width, height))

	return warp_reg
