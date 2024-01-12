# Tableau de bord des bornes Vélib en temps réel.
![image](https://github.com/ClementJosse/velib/assets/86595295/b00405ac-379c-405b-90d1-3688a214b3ac)

***Ce projet a besoin de Docker pour fonctionner.***

# Récupération du projet

## - via clone Github + docker build


#### Clone du projet
```
git clone git@github.com:ClementJosse/velib.git
```

#### Construire l'image Docker du projet
```
docker build -t velib .
```

## - via Docker hub
```
docker pull clementjosse/velib:latest
```
# Lancer le projet
```
docker run -p 8050:8050 velib
```
Le projet sera ensuite disponible à l'addresse 
http://localhost:8050/ de votre navigateur.
