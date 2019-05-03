# 3deposit #
3deposit is a 3D content preservation & publication platform. Key features include automated deposit metadata mapping, configurable storage & publication endpoints, and a content 'gallery builder'. 3deposit aims to be extensible, portable, and compatible with existing content preservation systems. 

## Storage ##
3deposit uses object storage. Instances can be configured to store objects locally or in a remote bucket. Remote buckets can be self-hosted with a MinIO server or with S3-compatbile services, such as AWS. 

## Publication ##
3deposit natively supports three media types:
* 3D models 
* 360 videos
* Virtual Reality applications

Media  | Publication Endpoint
------------- | -------------
3D models  | Sketchfab
360 Videos  | YouTube360
VR* | Surge.sh

*Properly configured WebVR applications will be published to static hosting. There is an experiemental feature to automatically port desktop VR applications to web-embeddable formats. 

## Data flow ##
![3deposit](./docs/3deposit-flow.png)