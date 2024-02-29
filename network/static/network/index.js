document.addEventListener("DOMContentLoaded", function () {
  // Agregar evento de click a todos los enlaces de "Editar"
  const editLinks = document.querySelectorAll(".edit-post");

  editLinks.forEach(function (editLink) {
    editLink.addEventListener("click", function (event) {
      // Detiene la acción predeterminada del enlace
      event.preventDefault();

      // Obtener el ID del post desde el atributo data-post-id
      const postId = editLink.getAttribute("data-post-id");

      // Encontrar el elemento del contenido del post
      const postContent = document.querySelector(`#post-content-${postId}`);

      // Crear un nuevo elemento <textarea> y llenarlo con el contenido actual del post
      const textarea = document.createElement("textarea");
      textarea.value = postContent.innerText.trim();
      textarea.id = `edit-textarea-${postId}`;
      textarea.className = "form-control";

      // Reemplazar el elemento original del contenido del post con el nuevo textarea
      postContent.replaceWith(textarea);

      // Ocultar el enlace "Editar" y mostrar el enlace "Guardar"
      document.getElementById(`edit-link-${postId}`).style.display = "none";
      document.getElementById(`save-link-${postId}`).style.display = "block";
    });
  });
});

function getCookie(name) {
  const cookieValue = document.cookie.match(`(^|;)\\s*${name}\\s*=\\s*([^;]+)`);
  return cookieValue ? cookieValue.pop() : "";
}

function saveChanges(postId) {
  // Obtener el contenido del textarea específico usando el ID único
  const textarea = document.getElementById(`edit-textarea-${postId}`);
  const newContent = textarea.value;

  fetch(`/edit_post/${postId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: `new_content=${encodeURIComponent(newContent)}`,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Actualizar el contenido original del post con el nuevo contenido
        // const postContent = document.getElementById(`post-content-${postId}`);
        const postContent = document.createElement("p");
        postContent.id = `post-content-${postId}`;
        postContent.innerText = newContent;

        // Reemplazar el textarea con el contenido original del post
        textarea.replaceWith(postContent);

        document.getElementById(`edit-link-${postId}`).style.display = "block";
        document.getElementById(`save-link-${postId}`).style.display = "none";
      } else {
        console.error(data.error);
      }
    })
    .catch((error) => console.error("Error:", error));
}

function toggleLike(postId, event) {
  event.preventDefault();

  fetch(`/toggle_like/${postId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.liked) {
        // Cambiar el corazón a rojo si el usuario dio like
        document.querySelector(
          `.like-post[data-post-id="${postId}"]`
        ).innerText = "❤️";
      } else {
        // Cambiar el corazón a azul si el usuario quitó el like
        document.querySelector(
          `.like-post[data-post-id="${postId}"]`
        ).innerText = "💙";
      }

      // Actualizar el conteo de likes
      document.getElementById(`like-count-${postId}`).innerText =
        data.like_count;
    })
    .catch((error) => console.error("Error:", error));
}
