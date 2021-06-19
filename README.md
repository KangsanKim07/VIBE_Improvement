# VIBE_Improvement
2021 Spring \<CS470 Introduction to Artificial Intelligence\> Final Project </br>
Replicate and improve [VIBE](https://arxiv.org/abs/1912.05656)
Code based on [@mkocabas/VIBE](https://github.com/mkocabas/VIBE) </br>
Four experiments to imporve VIBE
- Using adjacent frames for getting attention in the discriminator
- Put average of feature vectors as a prefix in the generator
- Using Transformer Encoder in the generator
- Giving identity to the body mesh

Please follow instruction of [@mkocabas/VIBE/doc/train.md](https://github.com/mkocabas/VIBE/blob/master/doc/train.md).
Our replication result is worse than VIBE because we couldn't use full data.


## Using adjacent frames for getting attention in the discriminator
In the paper, discriminator used self-attention to reflect importance of each frame. However, if one frame is important, its adjacent frames might be also important for the video. We adjust attention value using neighbor values. Attention value of frame i is: </br>
&alpha;<sub>i</sub> = (&alpha;<sub>i-1</sub> + &alpha;<sub>i</sub> + &alpha;<sub>i+1</sub>)/3 </br>
You can see my code at [lib/models/attention.py](https://github.com/KangsanKim07/VIBE_Improvement/blob/a5e6e820422f5dcc08e4bae1b34edd75dc018a86/lib/models/attention.py#L68).

|    | MPJPE | PA-MPJPE | PVE | ACCEL_ERR |
|:---:|:---:|:---:|:---:|:---:|
|VIBE|96.53| 63.92 | 116.50 | **28.58** |
|VIBE-adjacent|**93.31**| **62.80** | **115.96** | 30.45 |

## Put average of feature vectors as a prefix in the generator
We thought it would be better to give the context information before generating motions. Motion generator can understand what this video is about and reflect it to following generation. So we get average of feature vectors of all images and put it as a prefix. You can see my code at [lib/core/trainer.py](https://github.com/KangsanKim07/VIBE_Improvement/blob/a5e6e820422f5dcc08e4bae1b34edd75dc018a86/lib/core/trainer.py#L180).

<img src="https://user-images.githubusercontent.com/59245409/122636088-4adca700-d122-11eb-953d-2525f2130a56.png">

|    | MPJPE | PA-MPJPE | PVE | ACCEL_ERR |
|:---:|:---:|:---:|:---:|:---:|
|VIBE|96.53| 63.92 | **116.50** | **28.58** |
|VIBE-prefix|**93.38**| **62.76** | 123.00 | 31.01 |

## Combine two improvements
Our model shows more correct prediction specially for arms.

| <img src="https://user-images.githubusercontent.com/59245409/122636315-993e7580-d123-11eb-8206-ca3c235a5192.png" width="300" height="300">|  <img src="https://user-images.githubusercontent.com/59245409/122636324-a78c9180-d123-11eb-80e4-ec42970e293b.png" width="300" height="300"> | 
|:--:| :--:| 
| *VIBE* | *Ours* |

| <img src="https://user-images.githubusercontent.com/59245409/122636357-d86cc680-d123-11eb-849b-2ab6d7a6cb74.png" width="300" height="300">|  <img src="https://user-images.githubusercontent.com/59245409/122636378-f20e0e00-d123-11eb-8114-0503b18b5db4.png" width="300" height="300"> | 
|:--:| :--:| 
| *VIBE* | *Ours* |

|    | MPJPE | PA-MPJPE | PVE | ACCEL_ERR |
|:---:|:---:|:---:|:---:|:---:|
|VIBE|96.53| 63.92 | **116.50** | **28.58** |
|Ours|**93.38**| **62.76** | 123.00 | 31.01 |

## Using Transformer Encoder in the generator
We tried transformer encoder to use attention mechanism in the generator. Model can generate motions considering other frames. But it was worse than original VIBE for all metrics. I changed [lib/models/vibe.py](https://github.com/KangsanKim07/VIBE_Improvement/blob/a5e6e820422f5dcc08e4bae1b34edd75dc018a86/lib/models/vibe.py#L91)

|    | MPJPE | PA-MPJPE | PVE | ACCEL_ERR |
|:---:|:---:|:---:|:---:|:---:|
|VIBE|**126.69**| **83.41**| **148.75** | **23.26** |
|Ours|127.87| 90.33 | 163.89 | 31.79 |


## Giving identity to the body mesh
Same body mesh is used for different people even though their body shape are all different. We solve it by combining VIBE with [Neural Pose Transfer by Spatially Adaptive Instance Normalization](https://arxiv.org/abs/2003.07254)

#### Original output of VIBE
<img src="./images/1.gif" scale=0.5>

#### Fat identity
<img src="./images/2.gif" scale=0.5>

#### Thin identity
<img src="./images/3.gif" scale=0.5>
