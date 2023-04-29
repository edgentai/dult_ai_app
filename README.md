# dult_ai_app

Steps to run in VM

1. Launch a r4xlarge vm
2. Do a git pull
3. Install Docker on the machine, Follow the steps on - https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04

4. Install Docker compose using - https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04
5. Make the build file runnable by - sudo chmod +x ./scripts/build_grievance_handler.sh
6. sudo ./scripts/build_grievance_handler.sh
7. sudo docker-compose up
8. enter docker bash -- sudo docker exec -it grievance bash
9. python3 -m src.worker.start_grievance_worker
