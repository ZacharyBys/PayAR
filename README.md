# Stop being a payer, and start being a PayAR.

Products in the shop           |  Checkout center using Interac
:-------------------------:|:-------------------------:
![alt text](https://challengepost-s3-challengepost.netdna-ssl.com/photos/production/software_photos/000/755/359/datas/gallery.jpg) | ![alt text](https://challengepost-s3-challengepost.netdna-ssl.com/photos/production/software_photos/000/756/482/datas/gallery.jpg)

## Inspiration

We were always fascinated with AR, but were always too timid to get our hands dirty. We decided that at mchacks6, we would take the plunge and try something new. 

## What it does

PayAR is an augmented reality platform that allows users to enjoy an interactive shopping experience using their mobile device. 

As customers browse through the store, they can easily add items to their virtual carts through an immersive AR experience. Then, they can quickly pay for their purchase even before they collect it! Both clients and merchants are notified of the transaction through SMS.

## How we built it

We used Unity and Vuforia to create the augmented reality environment. We used Flask as our back-end framework to handle all of the business logic. We integrated Interac's E-Transfer API to handle payments and Twilio's API to handle SMS receipts. Finally, we hosted our data store in Azure.

## Challenges we ran into

We had difficulty integrating all the different components of our system together. Namely, connecting our back-end to the database hosted in Azure required a bit more than just a simple connection string. Additionally, creating high quality models for the AR component was a challenge due to difficult lighting conditions for photos, which were needed to generate these models.

## Accomplishments that we're proud of

We are very proud that we decided to take on something new for all of us, and that we were able to produce a functional proof-of-concept application. Furthermore, we could take advantage of these product databases to compare prices across retailers and suggest the best options.

## What we learned

We learned how to create augmented reality scenes using Vuforia and Unity. Most of the team had never touched either of these platforms, and so a lot of our development was in uncharted territory. 
We learned also about Interac and how effortless it is to send and receive money using their E-Transfer API.
Lastly, we learned a bit about using Azure to obtain resources in the cloud.

## What's next for PayAR

A possible next step for PayAR would be to integrate with large product data sets to pre-populate our product database and have to more extensive product details.
