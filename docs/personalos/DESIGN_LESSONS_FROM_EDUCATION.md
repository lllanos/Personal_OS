# PersonalOS — Lecciones de diseño desde Educación

## Propósito

Este documento registra los aprendizajes obtenidos durante la construcción iterativa del módulo Educación / Aprendizaje, especialmente Google Classroom, para evitar repetir los mismos errores en futuros dominios como Salud, Hogar, Finanzas o Documentación.

La regla central es:

> La estructura interna puede ser potente, pero la experiencia visible debe ser simple, guiada y accionable.

---

## 1. La base no debe ser la experiencia principal

Las bases de Notion son útiles para ordenar, relacionar, filtrar y consultar información, pero no deben ser el primer contacto del usuario común.

Error detectado:

- Abrir directamente una base tipo tabla para cargar Classroom.
- Mostrar campos estructurados antes de que el usuario entienda qué hacer.
- Forzar cambio de contexto visual.

Criterio corregido:

- La persona entra a una página guiada.
- La base queda como respaldo interno.
- La carga inicial debe poder hacerse sin abrir una tabla.

Patrón correcto:

```text
Página guiada
├── Ficha rápida visual
├── Seguimiento marcable
└── Base interna / registro avanzado
```

---

## 2. Una guía sin acción es ruido

No alcanza con decir qué hay que hacer. Cada instrucción importante debe tener una forma clara de avanzar, marcar, registrar o cerrar.

Error detectado:

- “Confirmar si usa Classroom, campus, Drive, WhatsApp, PDFs u otra fuente” quedaba como frase muerta.
- No había link, paso siguiente ni modo de cierre.

Criterio corregido:

- Toda recomendación debe convertirse en paso, enlace, checklist o ficha editable.
- Si algo debe hacerse, debe poder marcarse o completarse.

---

## 3. Los pasos deben navegar entre sí

Un flujo guiado no puede obligar al usuario a volver con la flecha del navegador.

Error detectado:

- Paso 1, Paso 2 y Paso 3 existían, pero no tenían navegación cruzada.

Criterio corregido:

Cada paso debe tener:

- Anterior, si aplica.
- Siguiente, si aplica.
- Volver al centro del dominio.
- Volver al Refugio / inicio.

Patrón correcto:

```text
Paso 1 → Paso 2 → Paso 3 → Cierre / Refugio
```

---

## 4. Las opciones no deben ser listas pasivas

Una lista de opciones ayuda a comprender, pero no permite actuar.

Error detectado:

- Google Classroom, Campus, Drive, WhatsApp, Email y PDFs aparecían como bullets sin destino.

Criterio corregido:

Cada opción relevante debe abrir una página de configuración específica o una acción concreta.

Patrón correcto:

```text
Elegí una fuente
├── Google Classroom → página guiada
├── Campus / Moodle → página guiada
├── Google Drive → página guiada
├── WhatsApp → página guiada
├── Email → página guiada
└── PDFs / Apuntes → página guiada
```

---

## 5. El usuario necesita campos visuales, no solo texto editable

En Notion, un bloque de texto puede editarse, pero no siempre se percibe como campo de entrada.

Error detectado:

- “Link de Classroom: pegar acá” no se sentía claramente como campo.
- El usuario tenía que interpretar dónde escribir.

Criterio corregido:

Cuando se espera que el usuario escriba información, usar una ficha visual tipo formulario.

Patrón recomendado:

```text
Ficha rápida visual
| Campo | Completar |
|---|---|
| Link de Classroom | pegar link aquí |
| Materia o clase | escribir aquí |
| Próxima acción | escribir aquí |
```

Esto no es un formulario técnico real, pero reduce ambigüedad visual.

---

## 6. El seguimiento debe estar dentro de la página guiada

El usuario debe saber cuándo puede considerar un bloque suficientemente terminado.

Error detectado:

- La página indicaba cosas a revisar, pero no tenía criterio de finalización.

Criterio corregido:

Cada flujo guiado debe tener una sección de seguimiento:

```text
Seguimiento para finalizar
- [ ] Tengo la fuente principal.
- [ ] Identifiqué el elemento principal.
- [ ] Revisé si hay fecha o entrega.
- [ ] Hay una próxima acción clara.
```

La perfección no es el objetivo. La claridad suficiente sí.

---

## 7. Fricción mínima para atención difusa

Para personas con atención dispersa o baja tolerancia a sistemas complejos, cada cambio de pantalla o formato aumenta la probabilidad de abandono.

Criterios obligatorios:

- No abrir bases como primera experiencia.
- No obligar a navegar hacia atrás.
- No dejar frases sin acción.
- No usar listas pasivas cuando se espera decisión.
- No pedir demasiados campos al inicio.
- No mostrar estructura interna antes de dar claridad.

Principio:

> La persona debe poder avanzar sin recordar cómo funciona el sistema.

---

## 8. Patrón obligatorio para futuros dominios

Todo nuevo dominio debe seguir este orden:

```text
Dominio
├── Página amable de entrada
├── Pregunta inicial simple
├── Flujo guiado
├── Ficha rápida visual
├── Seguimiento marcable
├── Navegación clara
└── Base interna / registro avanzado
```

Nunca iniciar por la base.

---

## 9. Aplicación directa al módulo Salud

Al construir Salud, evitar empezar con una tabla de turnos, estudios o medicación.

Patrón para Salud:

```text
Salud
├── ¿Qué necesitás organizar?
├── Turno médico / medicación / estudio / control / documento
├── Página guiada según opción
├── Ficha rápida visual
├── Seguimiento para finalizar
└── Registro interno
```

Ejemplo para turno médico:

```text
Ficha rápida visual
| Campo | Completar |
|---|---|
| Persona | escribir aquí |
| Especialidad | escribir aquí |
| Médico / institución | escribir aquí |
| Fecha / pendiente | escribir aquí |
| Qué llevar | escribir aquí |
| Próxima acción | escribir aquí |
```

Seguimiento mínimo:

- [ ] Sé para quién es.
- [ ] Sé qué tipo de turno es.
- [ ] Hay fecha o está claro que falta pedirla.
- [ ] Sé qué llevar o revisar.
- [ ] Hay próxima acción.

---

## 10. Regla final

Antes de crear cualquier nuevo módulo, preguntar:

1. ¿La persona entiende dónde empezar?
2. ¿Puede escribir lo importante sin abrir una base?
3. ¿Puede marcar avance?
4. ¿Puede pasar al siguiente paso sin volver atrás?
5. ¿Hay una próxima acción clara?
6. ¿La base está como soporte y no como experiencia principal?

Si alguna respuesta es “no”, el diseño todavía no está listo.
