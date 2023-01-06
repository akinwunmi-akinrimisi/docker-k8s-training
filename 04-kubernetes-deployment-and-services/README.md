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
- Canary deployment: uses a progressive delivery approach, with one version of the application serving most users, and another, newer version serving a small pool of test users. The test deployment is rolled out to more users if it is successful.
- Ramped slow rollout: rolls out replicas of the new version, while in parallel, shutting down old replicas. 
- Best-effort controlled rollout: specifies a “max unavailable” parameter which indicates what percentage of existing pods can be unavailable during the upgrade, enabling the rollout to happen much more quickly.

## Create a Deployment for our flask app
For this we will use a combination of the imperative and declarative methods to create a deployment for our flask app. This deployment should have 2 pods/replicas
- Run `kubectl create deploy flask-app-deploy --image=ghcr.io/emmanuelogiji/cloudboosta-flask-app:0.2.0 --replicas=2 --port=9900 --dry-run=client -o yaml > deploy.yaml`
- Update the deploy.yaml created to add some of our previous config like resources, enFrom, env and probes:
```diff
# deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: flask-app-deploy
  name: flask-app-deploy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flask-app-deploy
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: flask-app-deploy
    spec:
      containers:
      - image: ghcr.io/emmanuelogiji/cloudboosta-flask-app:0.2.0
        name: cloudboosta-flask-app
        ports:
        - containerPort: 9900
-       resources: {}
+       resources:
+         requests:
+           memory: "25Mi"
+           cpu: "250m"
+         limits:
+           memory: "50Mi"
+           cpu: "500m"
+       volumeMounts:
+         - name: config-volume
+           mountPath: /app/templates/
+       envFrom:
+       - configMapRef:
+           name: flask-config
+       env:
+       - name: AUTHOR
+         valueFrom:
+           secretKeyRef:
+             name: flask-secret
+             key: AUTHOR_NAME
+       startupProbe:
+         httpGet:
+           path: /author
+           port: 9900
+         failureThreshold: 30
+         periodSeconds: 10
+       readinessProbe:
+         tcpSocket:
+           port: 9900
+         initialDelaySeconds: 5
+         periodSeconds: 10
+       livenessProbe:
+         tcpSocket:
+           port: 9900
+         initialDelaySeconds: 15
+         periodSeconds: 20
+      volumes:
+      - name: config-volume
+        configMap:
+          name: mount-config
status: {}
```
- Run `kubectl create -f <path to deploy.yaml>` to create the deployment
- Run `kubectl get deploy,po` to see the state of the pods
- Inspect one of the deployment pods i.e. run `kubectl get po <pod name> -o yaml`
- Port forward to one of the deployment pods: `kubectl port-forward pod/<pod name> 9900:9900` and inspect the pages

## Carry out standard Deployment tasks
### Updating container image
Our deployment (and pods) are running the `ghcr.io/emmanuelogiji/cloudboosta-flask-app:0.2.0`. If this was an active project, what is likely is that new features will get added over time and these will be pushed as well to the registry.
The image `ghcr.io/emmanuelogiji/cloudboosta-flask-app:0.3.0` has been published with a small change to the /author page as a new feature.
Thus, for this exercise, we need to update our deployments (and pods) to point at this new image.
To do this:
- Run `kubectl set image deployment/flask-app-deploy cloudboosta-flask-app=ghcr.io/emmanuelogiji/cloudboosta-flask-app:0.3.0`
- Run `kubectl rollout status deployment/flask-app-deploy` to check the rollout status
- Run `kubectl get deploy,po` to see the state of the pods and see the progression
- Inspect one of the deployment pods i.e. run `kubectl get po <pod name> -o yaml`
- Port forward to one of the deployment pods: `kubectl port-forward pod/<pod name> 9900:9900` and inspect the pages


### Checking a deployment's rollout history
- Run `kubectl rollout history deployment/flask-app-deploy`

### Rolling back a deployment
Assuming there was an issue with an update, say we referenced an image version that didn't exist, we can roll back to a previous version.
- Run `kubectl rollout undo deployment/flask-app-deploy`. This would take the image version back to the previous one. You can add the `--to-revision` flag to roll back to a specific version i.e. `kubectl rollout undo deployment/flask-app-deploy --to-revision=1`
- You can track/inspect the progress using these:
  - Run `kubectl rollout status deployment/flask-app-deploy` to check the rollout status
  - Run `kubectl get deploy,po` to see the state of the pods and see the progression
  - Inspect one of the deployment pods i.e. run `kubectl get po <pod name> -o yaml`
  - Port forward to one of the deployment pods: `kubectl port-forward pod/<pod name> 9900:9900` and inspect the pages

### Scaling a deployment
Scaling a deployment up (increasing the number of replicas) or down (reducing the number of replicas) is important. You may need to scale up to have more pods because you have a lot of traffic to your application whilst when there is less traffic, you may want to scale down to save on compute costs.
To practice this,
- we will scale up our deployment to 4 replicas: Run `kubectl scale deployment/flask-app-deploy --replicas=4`
- we will scale the deployment back down to 2 replicas: Run `kubectl scale deployment/flask-app-deploy --replicas=2`

## Services
Services provide an abstract way to expose an application running on a set of Pods as a network service. 
With Pods able to change IP addresses frequently as a result of being restarted or recreated like during deployment rollouts, services give some stability whereby if you access an application by a service, you know that in the background, Kubernetes will get it to the correct pods/IPs provided everything is configured correctly.
Services are able to do this via selectors. Selectors are often label values. For example is you look at our deployment from our previous exercise, the label `app: flask-app-deploy` is set and is inherited by all pods spawned from the deployment.
Therefore, if we wanted a service for that deployment, it would use `app: flask-app-deploy` as a selector (a way to know which pods to forward requests to).
Services allow smooth interaction between different pods/deployments within a cluster or outside the cluster (to even human users).

There are three main Kubernetes service types:
- ClusterIP: Exposes the Service on a cluster-internal IP. Choosing this value makes the Service only reachable from within the cluster. This is the default that is used if you don't explicitly specify a type for a Service.
- NodePort: Exposes the Service on each Node's IP at a static port (the NodePort). This can be used to make a service reachable outside the cluster.
- LoadBalancer: Exposes the Service externally using a cloud provider's (e.g. AWS, Azure, GCP) load balancer. This can be used to make a service reachable outside the cluster


## Expose Deployments via Services
For this we are going to cover the following exercises
- Create a ClusterIP service for our flask app deployment
- Create a new pod in our cluster and access our flask app via the created Service
- Create a LoadBalancer service for our application and access it externally

### Create a ClusterIP service for our flask app deployment
We will expose the deployment with a Cluster IP service that points the service port 80 (default http port) to port 9900 which our deployment/pods expose
- Run `kubectl expose deployment flask-app-deploy --type=ClusterIP --port=80 --target-port=9900`
- Inspect the created service:
  - Run `kubectl get svc flask-app-deploy -o wide`. Note down the CLUSTER-IP value
  - Run `kubectl get svc flask-app-deploy -o yaml` to see what the yaml for a service looks like
  - Run `kubectl describe svc flask-app-deploy`

### Create a new pod in our cluster and access our flask app via the created Service
- We will use a nginx pod for this. To create that: Run `kubectl run nginx --image=nginx`
- We need to exec into the nginx pod, this will allow us run commands: Run `kubectl exec -it nginx -- sh`
- Use curl to access the service via the Cluster IP: Run `curl <CLUSTER-IP>:80`
- You should get the html for the homepage of our application
- **Optional** You can delete the pods from the deployment, allow them get recreated and repeat the above steps. It should still work exactly the same as even though Pod IPs have changed, the Service IP has not.


### Create a LoadBalancer service for our application and access it externally
- In a separate terminal, Run `minikube tunnel`
- On your regular terminal, Run `kubectl expose deployment flask-app-deploy --name=flask-app-lb --type=LoadBalancer --port=80 --target-port=9900`
- Run `kubectl get svc`. Notice that only the Load balancer service has an external IP
- On your browser, Go to `http://<EXTERNAL IP>:80`. We should get our application
