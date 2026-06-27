# PersonalOS — MVP Inicial

## 1. Propósito del MVP

El MVP inicial de **PersonalOS** busca crear una estructura simple, usable y liviana para organizar la vida personal y familiar desde una única página central.

El objetivo no es construir el sistema perfecto desde el inicio, sino una primera versión funcional que permita probar si PersonalOS reduce carga mental, mejora la visibilidad y evita que las tareas, fechas, documentos y decisiones importantes se pierdan.

El MVP debe responder rápidamente tres preguntas:

- **¿Qué está pasando?**
- **¿Qué hay que hacer ahora?**
- **¿Qué no puedo olvidarme?**

Para lograrlo, PersonalOS se organiza como una página principal visible para el usuario, sostenida por bases internas conectadas.

---

## 2. Principio de diseño del MVP

El MVP mantiene una decisión clave:

> **Una sola página para vivir el sistema. Bases internas para sostenerlo.**

Esto significa que el usuario no debería sentir que debe navegar por muchas páginas, bases o estructuras complejas. La experiencia principal debe ocurrir desde una única página llamada **PersonalOS** o **Centro de Control**.

Debajo de esa página pueden existir bases internas, relaciones y vistas filtradas, pero la interfaz de uso cotidiano debe ser simple, clara y directa.

---

## 3. Página principal: PersonalOS

La página principal funciona como centro de control personal y familiar.

Estructura recomendada:

```text
PersonalOS
│
├── Hoy / Ahora
├── No olvidar
├── Personas
├── Dominios de vida
├── Educación / Aprendizaje
├── Bloqueados
└── Captura rápida
```

Cada sección cumple una función concreta y debe ayudar al usuario a tomar acción sin esfuerzo.

---

## 4. Sección: Hoy / Ahora

Esta sección aparece al inicio de la página.

Su función es mostrar lo que requiere atención inmediata.

Debe incluir:

- Tareas vencidas.
- Tareas del día.
- Entregas próximas.
- Turnos próximos.
- Decisiones urgentes.
- Recordatorios críticos.
- Elementos bloqueados que requieren intervención.

Pregunta que responde:

> **¿Qué hay que hacer ahora?**

Esta sección debe ser breve, accionable y prioritaria. No debe convertirse en una lista infinita.

---

## 5. Sección: No olvidar

Esta sección contiene aquello que no necesariamente debe resolverse hoy, pero no puede perderse.

Ejemplos:

- Fechas de exámenes.
- Vencimientos.
- Turnos médicos.
- Pagos importantes.
- Documentos pendientes.
- Renovaciones.
- Inscripciones.
- Compromisos familiares.
- Responsabilidades recurrentes.

Pregunta que responde:

> **¿Qué no puedo olvidarme?**

Esta vista debe funcionar como memoria externa del sistema.

---

## 6. Sección: Personas

PersonalOS empieza por las personas.

Cada persona puede tener responsabilidades, dominios, tareas, documentos, fechas y decisiones asociadas.

Ejemplos de personas:

- Luis.
- Hijo mayor.
- Hija.
- Familia completa.
- Madre.
- Pareja.
- Otro familiar.

La página principal debe mostrar accesos simples a cada persona activa.

Cada persona puede tener su propia vista o subpágina, pero el acceso inicial debe mantenerse dentro del centro de control.

---

## 7. Sección: Dominios de vida

Los dominios son las grandes áreas que PersonalOS organiza.

Dominios iniciales recomendados:

- Educación.
- Salud.
- Hogar.
- Finanzas.
- Proyectos.
- Documentación.
- Familia.

No es necesario activar todos los dominios desde el inicio. El MVP debe permitir empezar con pocos y crecer progresivamente.

Cada dominio debe poder conectarse con personas, tareas, documentos, fechas, decisiones y elementos específicos.

---

## 8. Sección: Educación / Aprendizaje

Para el MVP inicial, **Educación / Aprendizaje** será el primer módulo real a validar.

Este módulo permite organizar:

- Personas que estudian.
- Materias.
- Cursos.
- Tareas.
- Entregas.
- Exámenes.
- Plataformas.
- Links.
- Documentos.
- Apuntes.
- Próximas acciones.

El módulo debe adaptarse al contexto de aprendizaje, no a una herramienta específica.

Tipos de aprendizaje contemplados:

- Colegio primario.
- Colegio secundario.
- Carrera universitaria o terciaria.
- Curso online.
- Capacitación laboral.
- Estudio personal.
- Otro.

La herramienta o plataforma se define después del contexto.

Ejemplos de plataformas:

- Google Classroom.
- Campus universitario.
- Moodle.
- Coursera.
- Udemy.
- Platzi.
- YouTube.
- Google Drive.
- Email.
- WhatsApp.
- PDFs o apuntes físicos.

---

## 9. Sección: Bloqueados

Esta sección muestra todo lo que no avanza porque falta algo.

Ejemplos de bloqueo:

- Falta una decisión.
- Falta un documento.
- Falta una fecha.
- Falta una respuesta.
- Falta acceso a una plataforma.
- Falta dinero.
- Falta responsable.
- Falta información.

Pregunta que ayuda a responder:

> **¿Qué está trabado y por qué?**

Esta sección es clave porque muchas responsabilidades no se pierden por falta de voluntad, sino porque quedan en un estado ambiguo.

---

## 10. Sección: Captura rápida

La captura rápida permite registrar información sin pensar demasiado.

Debe permitir cargar rápidamente:

- Una tarea.
- Una idea.
- Una fecha.
- Un documento.
- Una decisión.
- Un recordatorio.
- Un pendiente.

El objetivo es reducir fricción.

Si capturar algo requiere demasiado esfuerzo, el usuario volverá a usar la memoria, WhatsApp, notas sueltas o capturas de pantalla. Por eso esta sección debe ser simple y rápida.

---

## 11. Bases internas del MVP

Aunque el usuario vea una sola página, el sistema se sostiene con bases internas conectadas.

Bases recomendadas:

```text
Bases internas
│
├── Personas
├── Dominios
├── Elementos
├── Tareas
├── Documentos
└── Decisiones
```

Estas bases no deben sentirse pesadas para el usuario. Su propósito es sostener relaciones, filtros y vistas útiles.

---

## 12. Vistas esenciales

El MVP debe incluir estas vistas mínimas:

### Hoy / Ahora

Muestra tareas vencidas, tareas del día, entregas próximas, turnos y decisiones urgentes.

### No olvidar

Muestra recordatorios críticos, fechas importantes, vencimientos y compromisos futuros.

### Por persona

Permite ver todo lo relacionado con una persona específica.

### Por dominio

Permite revisar una dimensión completa de la vida, como Educación, Salud u Hogar.

### Bloqueados

Muestra todo lo que no avanza porque falta algo.

---

## 13. Flujo inicial recomendado

El onboarding inicial debe ser simple:

```text
1. ¿A quién querés organizar?
2. ¿Qué área querés organizar primero?
3. ¿Qué elemento concreto existe dentro de esa área?
4. ¿Hay alguna tarea, fecha, documento o decisión asociada?
5. ¿Cuál es la próxima acción?
```

Para el primer caso de uso, se recomienda iniciar con:

> **Educación / Aprendizaje de un hijo o hija.**

Es un caso cotidiano, fácil de validar y con mucho valor visible.

---

## 14. Criterios de éxito del MVP

El MVP funciona si:

- El usuario entra a una sola página y entiende qué mirar.
- Las tareas importantes no se pierden.
- Las fechas relevantes aparecen a tiempo.
- Las personas están claramente asociadas a sus responsabilidades.
- Las tareas tienen contexto.
- Los documentos importantes pueden encontrarse.
- Las decisiones pendientes quedan visibles.
- El sistema no se siente pesado.
- La captura rápida es más fácil que guardar todo en la memoria.

---

## 15. Criterios de fracaso

El MVP falla si:

- Requiere demasiados campos para cargar algo simple.
- Obliga al usuario a navegar por muchas páginas.
- Se convierte en archivo muerto.
- No muestra qué hacer ahora.
- No diferencia entre información, tarea, documento y decisión.
- Mantenerlo demanda más energía que el problema que intenta resolver.
- El usuario prefiere volver a notas sueltas, chats o memoria.

---

## 16. Conclusión

El MVP inicial de PersonalOS debe ser simple por fuera y estructurado por dentro.

La página principal debe funcionar como un centro de control claro, humano y accionable.

Las bases internas deben permitir relaciones, contexto y seguimiento sin exponer complejidad innecesaria.

La primera validación debe enfocarse en Educación / Aprendizaje, porque permite probar rápidamente la promesa central del sistema:

> Que nada importante se pierda, que todo tenga contexto y que siempre sea claro qué hacer después.
