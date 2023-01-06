# Kubernetes: Working with ConfigMaps and Secrets

This exercise has the following objectives:
- Understand what [Config Maps](https://kubernetes.io/docs/concepts/configuration/configmap/) and [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) are
- Difference between Config Map and Secrets
- Understand the concepts of [Imperative and Declarative object management](https://kubernetes.io/docs/concepts/overview/working-with-objects/object-management/)
- Create a config map with simple key-value pairs
- Create a secret with simple key-value pairs
- Configure a Pod to set environment variables using a secret/config map
- Create a config map from a file
- Mount a config map volume to a Pod as a means of setting up config files


## Difference between Config Map and Secrets
The major difference between config maps and secrets is that config maps are designed for non-sensitive values whilst secrets are designed for sensitive values such as passwords, API tokens and so on. 
This is why secrets employ base64 encryption. For all other intents and purposes, config maps and secrets can be used the same way.


## Understand the concepts of Imperative and Declarative object management
- What we have done previously (write yaml files (aka Kubernetes manifests) and then run `kubectl apply -f <file path>`) is the declarative approach
- The imperative approach involves using direct commands to create kubernetes objects e.g. using the command `kubectl run nginx --image=nginx --restart=Never` to create a nginx pod
- The two objects can be used in conjunction to allow for more speed/efficiency especially with the dry run option.
  - Consider the following example: You are tasked with creating an nginx pod with the environment variable `LOG_LEVEL` set to `WARNING`. You can do the following steps:
  - Run `kubectl run nginx --image=nginx --restart=Never --dry-run=client -o yaml > nginx.yaml`. This will give you a file named nginx.yaml with a Pod definition
  - Edit nginx.yaml to add the environment variable configuration:
     ```
      env:
      - name: LOG_LEVEL
        value: "WARNING"
     ```
  - Run `kubectl create -f nginx.yaml`
  - You have saved time as you have not had to write the entire contents of nginx.yaml from scratch
  - Delete the nginx pod now. Run `kubectl delete pod nginx`
- Imperative commands can be found under [kubectl commands](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands)


## Create a config map with simple key-value pairs
- For this, we want to create a config map called `flask-config` which has one key-value pair: LOG_LEVEL: INFO
- We will use the imperative method to create this config map by running: `kubectl create configmap flask-config --from-literal=LOG_LEVEL=INFO`
- If you run `kubectl get configmaps`, you will see your config map has been created.
- You can run `kubectl get configmap flask-config -o yaml` to see what the yaml would need to look like if you wanted to create this declaratively.
- You can also run `kubectl describe configmap flask-config` to see more details


## Create a secret with simple key-value pairs
- For this, we want to create a secret called `flask-secret` which has one key-value pair: AUTHOR_NAME: BIG_SECRET
- We will use the imperative method to create this secret by running: `kubectl create secret generic flask-secret --from-literal=AUTHOR_NAME=BIG_SECRET`
- If you run `kubectl get secrets`, you will see your config map has been created.
- You can also run `kubectl describe secret flask-secret` to see more details
  - You will notice that the value is not "BIG_SECRET". This is because as previously mentioned, Kubernetes secrets use base64 encryption.
  - You can copy the value there and base64 decode it to see. You can use a site like [this](https://www.base64decode.org/) or your terminal i.e. Run `echo <secret value> | base64 -d`


## Configure a Pod to set environment variables using a secret/config map
- [Configure a Pod to Use a ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/)
- In this task we want to do the following with our Flask app pod:
  - Set up our pod to have all keys of the config map `flask-config` set as environment variables
  - Set up our pod to have the environment variable `AUTHOR` set to the value of the `AUTHOR_NAME` key in the `flask-secret` secret


### Set up our pod to have all keys of the config map `flask-config` set as environment variables
- Update your last pod.yaml from chapter 2 to remove the LOG_LEVEL env setting and add an envFrom setting to reference the config map:

```diff
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-flask-app
spec:
  containers:
  - name: my-flask-app
    image: ghcr.io/emmanuelogiji/cloudboosta-flask-app:0.2.0
    ports:
    - containerPort: 9900
    resources:
      requests:
        memory: "25Mi"
        cpu: "250m"
      limits:
        memory: "50Mi"
        cpu: "500m"
+   envFrom:
+   - configMapRef:
+       name: flask-config
    env: 
-   - name: LOG_LEVEL
-     value: "DEBUG"
    - name: AUTHOR
      value: "Pod"
    startupProbe:
      httpGet:
        path: /author
        port: 9900
      failureThreshold: 30
      periodSeconds: 10
    readinessProbe:
      tcpSocket:
        port: 9900
      initialDelaySeconds: 5
      periodSeconds: 10
    livenessProbe:
      tcpSocket:
        port: 9900
      initialDelaySeconds: 15
      periodSeconds: 20
```

- Recreate the pod `kubectl create -f <path to pod.yaml>`
- To confirm, 
  - Run `kubectl exec -it my-flask-app -- sh` to exec into the pod
  - Run `echo $LOG_LEVEL` to check the value of the environment variable. This should be INFO as we set when creating our config map
  - Type `exit` and press enter when done to close the shell
- You can then delete the pod before the next exercise: `kubectl delete pod my-flask-app`

### Set up our pod to have the environment variable `AUTHOR` set to the value of the `AUTHOR_NAME` key in the `flask-secret` secret
- Update your pod.yaml from the last exercise as follows:
- Update your last pod.yaml from chapter 2 to remove the LOG_LEVEL env setting and add an envFrom setting to reference the config map:

```diff
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-flask-app
spec:
  containers:
  - name: my-flask-app
    image: ghcr.io/emmanuelogiji/cloudboosta-flask-app:0.2.0
    ports:
    - containerPort: 9900
    resources:
      requests:
        memory: "25Mi"
        cpu: "250m"
      limits:
        memory: "50Mi"
        cpu: "500m"
    envFrom:
    - configMapRef:
        name: flask-config
    env: 
    - name: AUTHOR
-     value: "Pod"
+     valueFrom:
+       secretKeyRef:
+         name: flask-secret
+         key: AUTHOR_NAME  
    startupProbe:
      httpGet:
        path: /author
        port: 9900
      failureThreshold: 30
      periodSeconds: 10
    readinessProbe:
      tcpSocket:
        port: 9900
      initialDelaySeconds: 5
      periodSeconds: 10
    livenessProbe:
      tcpSocket:
        port: 9900
      initialDelaySeconds: 15
      periodSeconds: 20
```
- Recreate the pod `kubectl create -f <path to pod.yaml>`
- To confirm, 
  - Run `kubectl exec -it my-flask-app -- sh` to exec into the pod
  - Run `echo $AUTHOR` to check the value of the environment variable. This should be BIG_SECRET as we set when creating our secret
  - Type `exit` and press enter when done to close the shell
- You can then delete the pod before the next exercise: `kubectl delete pod my-flask-app`

## Create a config map from a file
- For this we are going to create a new default.html template file and then create a config map from it.
- Create and save a new file called default.html file with the content:
```html
<!DOCTYPE html>
<html lang="en">

<body>
<h2 align="center">This is a simple flask app homepage that has been overwritten via Config Map!</h2>
</body>
</html>
```
- Create a config map called `mount-config` from this file using the command `kubectl create configmap mount-config --from-file=<path to new default.html>`
- If you run `kubectl get configmaps`, you will see your config map has been created.
- You can run `kubectl get configmap mount-config -o yaml` to see what the yaml would need to look like if you wanted to create this declaratively.
- You can also run `kubectl describe configmap mount-config` to see more details

## Mount a config map volume to a Pod as a means of setting up config files
[Adding ConfigMap data a volume](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#add-configmap-data-to-a-volume) allows you to add config files for an application without changing the underlying application or even the container in this case.
If you remember our flask app, it renders the `templates/default.html` file as the homepage. 
In this exercise, we are going to use the config map which we just created to overwrite the default.html template in the container.
To do this,
- we need to update our pod definition (from the last exercise) to be as follows:
```diff
apiVersion: v1
kind: Pod
metadata:
  name: my-flask-app
spec:
  containers:
  - name: my-flask-app
    image: ghcr.io/emmanuelogiji/cloudboosta-flask-app:0.2.0
    ports:
    - containerPort: 9900
    resources:
      requests:
        memory: "25Mi"
        cpu: "250m"
      limits:
        memory: "50Mi"
        cpu: "500m"
+   volumeMounts:
+     - name: config-volume
+       mountPath: /app/templates/
    envFrom:
    - configMapRef:
        name: flask-config
    env:
    - name: AUTHOR
      valueFrom:
        secretKeyRef:
          name: flask-secret
          key: AUTHOR_NAME
    startupProbe:
      httpGet:
        path: /author
        port: 9900
      failureThreshold: 30
      periodSeconds: 10
    readinessProbe:
      tcpSocket:
        port: 9900
      initialDelaySeconds: 5
      periodSeconds: 10
    livenessProbe:
      tcpSocket:
        port: 9900
      initialDelaySeconds: 15
      periodSeconds: 20
+ volumes:
+ - name: config-volume
+   configMap:
+     name: mount-config
```
- Recreate the pod `kubectl create -f <path to pod.yaml>`
- To confirm,
  - Port forward to the container port: `kubectl port-forward pod/my-flask-app 9900:9900`
  - Go to `localhost:9900` and `localhost:9900/author` on your browser and see that the homepage has been updated