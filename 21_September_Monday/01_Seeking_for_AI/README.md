# The Whole Story

## The real or virtual world

`parameters -> [ Instrument or Simulation ] -> measurement`

## The AI World

`X -> [ AI ] -> Y`

The AI is a model with many internal 'weights'.

- The **training** consists in correlating 'X' and 'Y'. The implementation uses e.g. 'gradient back-propagation' to minimise a 'loss' function. 
- The **inference** consists in inputting new 'X' and get corresponding 'Y'.

## AI categories

There are 4 different AI 'algorithm' types.


| AI            | X=parameters | X=measurement |
| --------------|--------------|----------------|
| **Y=parameters**  | optimisation         | inverse problem: classification/regression |
| **Y=measurement** | surrogate/simulation | denoising/segmentation/deconvolution |
