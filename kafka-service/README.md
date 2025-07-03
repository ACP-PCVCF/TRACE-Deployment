## Kafka – Usage and Access

Kafka is deployed in the proving-system namespace using the Bitnami Helm Chart. This is done automatically via the setup.sh script (you don't have to execute this again):

```bash
helm install kafka bitnami/kafka \
  --namespace proving-system \
  --create-namespace \
  -f kafka-service/kafka-values.yaml
```

After deployment, the Kafka broker is accessible within the cluster at `kafka.proving-system.svc.cluster.local:9092`.

### Access and Testing

To interact with the Kafka broker, a temporary client pod can be started:

```bash
kubectl run kafka-test-client --rm -it --restart=Never \
  --image=bitnami/kafka --namespace=proving-system -- bash
```

From inside the pod, the following commands can be used:

#### List all topics:

```bash
kafka-topics.sh --bootstrap-server kafka.proving-system.svc.cluster.local:9092 --list
```

#### Read messages from specific topics (here shipments):

```bash
kafka-console-consumer.sh \
  --bootstrap-server kafka.proving-system.svc.cluster.local:9092 \
  --topic shipments \
  --from-beginning \
  --max-messages 10
```

#### Exit:

```bash
exit
```

The pod will be automatically removed upon exit.

git remote add -f verifier-service https://github.com/ACP-PCVCF/verifier.git  
git subtree add --prefix=verifier-service verifier-service main --squash
