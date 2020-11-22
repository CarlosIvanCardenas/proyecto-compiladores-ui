# UI proyecto compiladores: **Lenguaje Dale++**
Interfaz gráfica para el lenguaje Dale++, el cual lo convierte en un lenguaje de programación visual basado en bloques.

La carpeta **./core** contiene un fork del repositorio: https://github.com/CarlosIvanCardenas/proyecto-compiladores
donde se encuentra toda la funcionalidad clave del compilador.

## Avances actuales 
### Compilador
- Se desarrollaron las **expresiones regulares** y las **gramáticas** del lenguaje Dale++
- Se desarrolló el **lexer** del lenguaje Dale++ basándose en las expresiones regulares previamente desarrolladas.
- Se desarrolló el **parser** del lenguaje Dale++ basándose en las gramáticas previamente desarrolladas.
- Se desarrolló el **directorio de procedimientos** y la **table de variables**
- Se añadieron **acciones semanticas** para la creación de **directorio de procedimientos** y **tabla de variables**.
- Se añadieron **acciones semanticas** para la creación de código de **expresiones aritmeticas**.
- Se añadieron **acciones semanticas** para la creación de código de **estatutos secuenciales**.
- Se añadieron **acciones semanticas** para la creación de código de **estatutos condicionales de decision**.
- Se añadieron **acciones semanticas** para la creación de código de **estatutos condicionales de ciclos**.
- Se añadieron **acciones semanticas** para la creación de código de **declaración de funciones**.
- Se añadieron **acciones semanticas** para la creación de código de **llamadas a funciones**.
- Se añadió el componente de **memoria** para asignar **direcciones** en los quads.
- Se añadieron **acciones semanticas** para la declaración de **arreglos**.
- Se añadieron **acciones semanticas** para el uso de **arreglos**.

### Máquina Virtual
- Se desarrolló la **memoria** para la maquina virtual.
- Se añadieron funciones para el manejo de todas las **instrucciones** que genera el compilador.
- Se desarrollo el **flujo de los cuadruplos** para su ejecución.
- Se desarrollo el **stack de ejecución**.

### Interfaz Gráfica
- Se añadieron todos los **bloques** necesarios para la gramática del lenguaje.
- Se desarrolló la **generación de código a partir de los bloques** en el workspace.
- Se incluyo **verificación de tipo de dato** en los bloques.
- La interfaz ejecuta el compilador como un proceso hijo y le envia el código generado.
- La interfaz maneja las entradas y salidas del compilador.
- Se incluyo soporte para **guardar y cargar programas** de un archivo .txt
