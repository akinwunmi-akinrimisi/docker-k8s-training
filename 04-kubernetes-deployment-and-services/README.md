# Kubernetes: Working with Deployments and Services

This exercise has the following objectives:
- Understand why [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) are needed and preferred to Pods
- Understand the different Deployment strategies
- Create a Deployment for our flask app
- Carry out standard Deployment tasks:
  - Updating container image
  - Checking a deployment's rollout history
  - Rolling back a deployment
  - Scaling a deployment
- Understand what [Services](https://kubernetes.io/docs/concepts/services-networking/service/) are and the types of services
- Expose Deployments via Services
- Understand [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)


## Why Deployments are needed and preferred to Pods
Deployments offer a level of abstraction over Pods. This means we can update a Pod or group of Pods centrally and have th changes trickle down rather than having to delete and recreate like we have been doing.
Deployments afford us the ability to do the following:
- Run multiple pods for one application
- Scale the number of application pods up or down 
- Update every running application pod
- Roll back all application pods to another version

## Deployment Strategies
Reproduced from [here](https://spot.io/resources/kubernetes-autoscaling/5-kubernetes-deployment-strategies-roll-out-like-the-pros/)
- Rolling deployment: replaces pods running the old version of the application with the new version, one by one, without downtime to the cluster.
- Recreate: terminates all the pods and replaces them with the new version.
- Ramped slow rollout: rolls out replicas of the new version, while in parallel, shutting down old replicas. 
- Best-effort controlled rollout: specifies a “max unavailable” parameter which indicates what percentage of existing pods can be unavailable during the upgrade, enabling the rollout to happen much more quickly.
- Canary deployment: uses a progressive delivery approach, with one version of the application serving most users, and another, newer version serving a small pool of test users. The test deployment is rolled out to more users if it is successful.

## Create a Deployment for our flask app

## Carry out standard Deployment tasks