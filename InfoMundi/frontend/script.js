const API_PAISES = "https://restcountries.com/v3.1/name/";
const API_LOCAL = "http://127.0.0.1:8000/favoritos";
const API_CLEANED = "http://127.0.0.1:8000/api/cleaned_data";

// Buscar país desde la API externa
async function buscarPais() {
  const nombre = document.getElementById("input-pais").value.trim();
  if (!nombre) return alert("Escribí un nombre de país");

  try {
    const res = await fetch(`${API_PAISES}${nombre}`);
    const data = await res.json();

    mostrarResultados(data);
  } catch (error) {
    alert("No se pudo buscar el país 😢");
    console.error(error);
  }
}

// Mostrar resultados de la búsqueda
function mostrarResultados(paises) {
  const contenedor = document.getElementById("resultados");
  contenedor.innerHTML = "";

  paises.forEach((pais) => {
    const nombre = pais.name.common;
    const capital = pais.capital?.[0] || "Desconocida";
    const continente = pais.continents?.[0] || "Desconocido";
    const bandera = pais.flags?.png || pais.flags?.svg || "";

    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <img src="${bandera}" alt="Bandera de ${nombre}" />
      <h3>${nombre}</h3>
      <p><strong>Capital:</strong> ${capital}</p>
      <p><strong>Continente:</strong> ${continente}</p>
      <button onclick="guardarFavorito('${nombre}', '${bandera}')">💾 Guardar favorito</button>
    `;

    contenedor.appendChild(card);
  });
}

// Guardar país favorito en la API local
async function guardarFavorito(nombre, imagen_url) {
  const comentario = prompt(`¿Por qué te gusta ${nombre}? 📝`);

  if (!comentario) return alert("Favorito cancelado.");

  try {
    const res = await fetch(API_LOCAL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre, comentario, imagen_url }),
    });

    if (!res.ok) throw new Error("Error al guardar favorito");

    alert("✅ ¡Favorito guardado!");
    cargarFavoritos(); // actualizar la lista
    cargarDatosLimpios(); // refrescar los datos limpios
  } catch (error) {
    alert("No se pudo guardar 😓");
    console.error(error);
  }
}

// Cargar favoritos desde la API local
async function cargarFavoritos() {
  try {
    const res = await fetch(API_LOCAL);
    const favoritos = await res.json();

    const contenedor = document.getElementById("favoritos");
    contenedor.innerHTML = "";

    favoritos.forEach((fav) => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div class="bandera">
          <img src="${fav.imagen_url}" alt="Imagen de ${fav.nombre}" />
        </div>
        <h3>${fav.nombre}</h3>
        <p><strong>Comentario:</strong> ${fav.comentario}</p>
      `;
      contenedor.appendChild(card);
    });
  } catch (error) {
    console.error("Error al cargar favoritos", error);
  }
}

// ========================
// Cargar datos limpios (cleaned_data)
// ========================
async function cargarDatosLimpios() {
  try {
    const res = await fetch(API_CLEANED);
    const data = await res.json();

    const tableBody = document.querySelector("#cleanedTable tbody");
    tableBody.innerHTML = ""; // limpiar antes de cargar

    data.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.id}</td>
        <td>${row.nombre}</td>
        <td>${row.pais}</td>
        <td>${row.fecha ? row.fecha : "-"}</td>
        <td>${row.valor ?? "-"}</td>
        <td>${row.fuente ?? "-"}</td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (error) {
    console.error("Error al cargar datos limpios", error);
  }
}

// Cargar todo al iniciar
window.onload = () => {
  cargarFavoritos();
  cargarDatosLimpios();
};

