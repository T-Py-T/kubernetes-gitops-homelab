#!/bin/bash

echo "✅ Kubectl and Helm installed successfully"

udo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx
sudo ln -s /opt/kubectx/kubens /usr/local/bin/kubens
brew install derailed/k9s/k9s

echo "✅ kubectx, kubens, fzf, and k9s installed successfully"
sudo apt-get install fzf -y

alias k="kubectl"
alias kga="kubectl get all"
alias kgn="kubectl get all --all-namespaces"
alias kdel="kubectl delete"
alias kd="kubectl describe"
alias kg="kubectl get"

echo 'alias k="kubectl"' >> /home/$USER/.bashrc
echo 'alias kga="kubectl get all"' >> /home/$USER/.bashrc
echo 'alias kgn="kubectl get all --all-namespaces"' >> /home/$USER/.bashrc
echo 'alias kdel="kubectl delete"' >> /home/$USER/.bashrc
echo 'alias kd="kubectl describe"' >> /home/$USER/.bashrc
echo 'alias kg="kubectl get"' >> /home/$USER/.bashrc

echo "✅ The following aliases were added:"
echo "alias k=kubectl"
echo "alias kga=kubectl get all"
echo "alias kgn=kubectl get all --all-namespaces"
echo "alias kdel=kubectl delete"
echo "alias kd=kubectl describe"
echo "alias kg=kubectl get"

source ~/.bashrc 


# DevContainer setup script
set -e

echo "🔧 Setting up Kubernetes test environment..."

# Install kustomize
echo "📦 Installing kustomize..."
curl -s https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh | bash
sudo mv kustomize /usr/local/bin/

# Verify all tools
echo "✅ Tool versions:"
kubectl version --client --short
helm version --short
minikube version --short  
kustomize version --short

echo ""
echo "🚀 Ready! Use these commands:"
echo "  minikube start                           # Start cluster"
echo "  kustomize build . --enable-helm         # Test build"
echo "  ./test.sh                                # Run full test"