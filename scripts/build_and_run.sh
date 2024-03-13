echo "____Building image..."
sudo docker build --tag agreemod .
echo "____Stopping old container..."
sudo docker stop agreemod
echo "____Removing old container..."
sudo docker rm agreemod
echo "____Starting service as a new container..."
sudo docker run -d --network=host --name agreemod --restart always agreemod
