#### collaboration
* Bruce will make PR with DISCUSSION.txt or md and make it a PR against my fork for discussion
* Bruce will make PR for NumericArray for discussion

#### demo
* Bruce will quickly run through demos to make sure we're on same page
* quick tour of demo code, maybe

#### NumericArrayListExpr
* dead end, abandon in favor of NumericArray

---
TUES NOV 11

#### NumericArray

* Codex impl is at https://chatgpt.com/codex/tasks/task_e_6909b81266188330b5b22bac0b27c272 - a couple questions there are useful general info for Bruce, so let's take a look
* Ditto https://github.com/bdlucas1/mathics-core/tree/codex/implement-mathematica-numericarray-with-numpy
* NumericArray trial balloon: https://github.com/bdlucas1/mathics-core/pull/3 - Bruce thinks this is the right direction, but need high-level review for sanity of overall organization from Rocky
* PR https://github.com/Mathics3/mathics-core/pull/1512/files
* Note: GraphicsComplex[3D] using NumericArray is nonstandard afaics, but seems perfectly reasonable
* Consumers of Graphics3D will need to be updated to understand GraphicsComplex and NumericArray
    * external - front-ends
    * internal - boxing, formatting
    * can we add a global switch to enable the new impl (default off) to ease transition? where?

#### compile
* as per email abandoning writing own compiler directly from Mathics to Python. Instead will use to_sympy and sympy.lambdify.
* how to test
    * maybe monkey-patch "evaluate" to be "compile and run" and re-use existing tests

#### upcoming PRs
* beef up tests for Plot3D to check structure of Graphics3D output, in preparation for following
* refactoring of eval_Plot3D without change of function, in preparation for following
* addition of option for eval_Plot3D to generate Graphics3D with GraphicsComplex and NumericArray
* https://github.com/bdlucas1/mathics-core/pull/7: to_sympy in If to support If in plotting expressions
* https://github.com/bdlucas1/mathics-core/pull/8: make SympyExpression iterable to support Hypergeometric in plotting
* utilities for printing mathics expressions and sympy expressions as indented trees
* timer utility

#### layout
* architecture ok?
* analgous to format, but data structure instead of string
    * any value to merging with format?
* dash vs ipywidgets
* repository organization
    * how to reuse across front-ends
* how to package front-ends
* jupyter/jupyterlite packaging - kernel
* how to use in shell front-end
* need browser front-end given jupyter?

#### Graphics3D
* need GraphicsComplex for performance, but support across the board?
    * with NumpyArrayListExpr or NumericArray?
* boxing currently not standard
* needs considerable build-out itself
* how to test

#### Plot3D
* needs considerable build-out
* how to test
* deploy unconditionally or conditionally
    * former requires support across the board

#### ComplexPlot3D, etc
* identify others that uses Graphics3D and build out

#### Graphics (2d)
* GraphicsComplex needed?
* support across the board?

#### Manipulate
* non-standard ManipulateBox vs DynamicModule, Dymanic, Dynamic*Box, etc.
* other functions like Animate?

