# Ejemplo del subconjunto de Python aceptado por el traductor.

class Contador:
    def __init__(self, inicio):
        self.valor = inicio

    def incrementar(self, cantidad):
        self.valor = self.valor + cantidad
        return self.valor


def saludar(nombre):
    print("Hola, " + nombre)


contador = Contador(0)
saludar("equipo")

for numero in range(1, 4):
    print(numero)

while contador.valor < 5:
    contador.incrementar(1)

if contador.valor == 5:
    print("¡Meta alcanzada!")
else:
    print("Aún falta")
