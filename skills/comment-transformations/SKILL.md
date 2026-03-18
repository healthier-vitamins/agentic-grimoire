# Comment Transformations

Use this skill for dense or non-obvious transformations.

## Objective

Help future readers understand tricky logic quickly.

## Add comments when

- string transformation is non-obvious
- array/object reshaping is compact or multi-step
- regex behavior is easy to misread
- parsing/mapping/filtering logic is dense
- encoded values are being normalized

## Comment style

- show short example input
- show the transformation result
- keep it brief and accurate

Example:

```ts
// input: "alpha,beta,gamma"
const firstTwo = value.split(",").slice(0, 2);
// output: ["alpha", "beta"]
```

D
