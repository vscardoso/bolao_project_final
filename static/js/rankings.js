// JavaScript para inicializar as barras de progresso na tabela de classificação

document.addEventListener('DOMContentLoaded', function() {
    console.log("Rankings script loaded"); // Para debug
    
    // Encontre o valor máximo de pontos (primeiro lugar)
    const pointsCells = document.querySelectorAll('.table tbody tr .fw-bold');
    console.log("Found points cells:", pointsCells.length); // Para debug
    
    if (pointsCells.length === 0) return;
    
    const maxPoints = parseInt(pointsCells[0].textContent) || 0;
    console.log("Max points:", maxPoints); // Para debug
    
    if (maxPoints === 0) return; // Evita divisão por zero
    
    // Adicione barras de progresso a cada célula de pontos
    pointsCells.forEach((pointsCell, index) => {
        const points = parseInt(pointsCell.textContent) || 0;
        const percentage = (points / maxPoints) * 100;
        console.log(`User ${index+1}: ${points} points (${percentage.toFixed(1)}%)`); // Para debug
        
        const bar = document.createElement('div');
        bar.className = 'points-bar';
        
        const fill = document.createElement('div');
        fill.className = 'points-bar-fill';
        fill.style.width = `${percentage}%`;
        
        bar.appendChild(fill);
        pointsCell.parentNode.appendChild(bar);
    });
});