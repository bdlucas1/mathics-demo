import argparse
import core
import sym
import layout as lt
import util
import dash.dcc
import os
import sys
import cv2
import threading

parser = argparse.ArgumentParser(description="Mathics3 graphics test")
#parser.aad_argument("--accept", type=bool, action-"store_true")
parser.add_argument("files", type=str, default=None, nargs="*")
args = parser.parse_args()

class FE:
    pass
fe = FE()

fe.session = core.MathicsSession()

def differ(im1, im2):
    im1 = cv2.imread(im1) if os.path.exists(im1) else None
    im2 = cv2.imread(im2) if os.path.exists(im2) else None
    
    difference = None

    if im1 is None:
        difference = "im1 does not exist"
    elif im2 is None:
        difference = "im2 does not exist"
    elif im1.shape != im2.shape:
        difference = f"image shapes {im1.shape} {im2.shape} differ"
    elif not (im1 - im2 == 0).all():
        difference = f"images differ"

    if difference:
        if im1 is not None: cv2.imshow("im1", im1)
        if im2 is not None: cv2.imshow("im2", im2)
        if im1 is not None and im2 is not None: cv2.imshow("diff", abs(im2-im1))
        print(difference)
        print("press any key to continue")
        cv2.waitKey(0)
    else:
        print("images are identical")

    return difference

failures = 0
successes = 0

for fn in args.files:

    fn_m = fn.replace(".png", ".m")
    fn_ref = fn.replace(".m", ".png")
    fn_test = "/tmp/test.png"

    print(f"=== {fn_m}")

    if os.path.exists(fn_test):
        os.remove(fn_test)

    fe.test_image = fn_test
    with open(fn_m) as f:
        s = f.read()
    expr = fe.session.parse(s)
    expr = expr.evaluate(fe.session.evaluation)
    layout = lt.expression_to_layout(fe, expr)

    if differ(fn_ref, fn_test):
        failures += 1
        response = input("update reference image? (y/n): ")
        if response == "y":
            print(f"updating reference image {fn_ref}")
            with open(fn_test, "rb") as f_test:
                img_data = f_test.read()
                with open(fn_ref, "wb") as f_ref:
                    f_ref.write(img_data)
    else:
        successes += 1

print(f"=== {successes} successes, {failures} failures")                    
