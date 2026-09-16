# The Whole Story

## The real or virtual world

`parameters -> [ Instrument or Simulation ] -> measurement`

## The AI World

`X -> [ AI ] -> Y`

The AI is a model with way-many internal 'weights'.

- The **training** consists in correlating 'X' and 'Y'. The methodology uses e.g. 'gradient backpropagation'. 
- The **inference** consists in inputing new 'X' and get corresponding 'Y'.

## AI categories

There are 4 different AI 'algorithm' types.


| AI            | X=parameters | X=measurement |
| --------------|--------------|----------------|
| **Y=parameters**  | optimisation         | inverse problem |
| **Y=measurement** | surrogate/simulation | denoising/segmentation/deconvolution |
