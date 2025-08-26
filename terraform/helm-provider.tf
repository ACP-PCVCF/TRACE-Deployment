data "azurerm_kubernetes_cluster" "demo" {
  name                = azurerm_kubernetes_cluster.default.name
  resource_group_name = azurerm_resource_group.default.name
}

provider "helm" {
  kubernetes = {
    host                   = data.azurerm_kubernetes_cluster.demo.kube_config[0].host
    client_certificate     = base64decode(data.azurerm_kubernetes_cluster.demo.kube_config[0].client_certificate)
    client_key             = base64decode(data.azurerm_kubernetes_cluster.demo.kube_config[0].client_key)
    cluster_ca_certificate = base64decode(data.azurerm_kubernetes_cluster.demo.kube_config[0].cluster_ca_certificate)
  }
}

resource "helm_release" "TRACE" {
  name       = "TRACE"
  namespace  = "default"
  repository = "https://acp-pcvcf.github.io/TRACE-Deployment/"
  chart      = "TRACE"
  values     = [file("../charts/TRACE/values.yaml")]
}

