# docker build -t oms-server .
# docker run --env-file=.env -i -t -p 4000:4000 oms-server

kubectl apply -f ./server/server-deployment.yaml
kubectl apply -f ./server/server-service.yaml
kubectl apply -f ./server/ingress.yaml

kubectl apply -f ./router/router-deployment.yaml
kubectl apply -f ./router/notifier-deployment.yaml
kubectl apply -f ./router/categorizer-deployment.yaml

kubectl apply -f ./rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f ./rabbitmq/rabbitmq-service.yaml

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml