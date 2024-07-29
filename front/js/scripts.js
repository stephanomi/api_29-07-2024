document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    let formData = new FormData();
    formData.append('topic_name', document.getElementById('topic_name').value);
    formData.append('file1', document.getElementById('file1').files[0]);
    formData.append('file2', document.getElementById('file2').files[0]);

    // Obtener los botones
    const submitButton = document.querySelector('button[type="submit"]');
    const downloadButton = document.getElementById('downloadBtn');
    const refreshButton = document.getElementById('refreshBtn');
    
    // Ocultar el botón de enviar
    submitButton.style.display = 'none';
    
    // Mostrar la barra de carga
    document.getElementById('loading').style.display = 'block';
    document.getElementById('response').innerText = '';

    try {
        let response = await fetch('http://127.0.0.1:5000/process', {
            method: 'POST',
            body: formData
        });
        
        // Ocultar la barra de carga
        document.getElementById('loading').style.display = 'none';
        
        if (response.ok) {
            let data = await response.json();
            document.getElementById('response').innerText = data.estado_del_arte;
            // Habilitar y cambiar el estilo del botón de descarga
            downloadButton.disabled = false;
            downloadButton.classList.remove('btn-secondary');
            downloadButton.classList.add('btn-primary');
            // Habilitar y cambiar el estilo del botón de refrescar
            refreshButton.style.display = 'inline-block';
            refreshButton.disabled = false;
            refreshButton.classList.remove('btn-secondary');
            refreshButton.classList.add('btn-primary');
        } else {
            let errorData = await response.json();
            document.getElementById('response').innerText = `Error: ${errorData.error}`;
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('response').innerText = 'Error al conectar con la API';
    }
});

function descargarResultado() {
    const responseText = document.getElementById('response').innerText;
    if (!responseText) {
        alert('No hay nada para descargar');
        return;
    }

    const blob = new Blob([responseText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resultado.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
