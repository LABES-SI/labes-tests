
const { test, expect } = require('@playwright/test');

test.describe('QA07 - Análise Temporal da Infraestrutura', () => {

  test('QA07-01 - Deve acessar a página de análise temporal', async ({ page }) => {
    const response = await page.goto(
      '/indicadores/infraestrutura/analise-temporal'
    );

    expect(response).not.toBeNull();
    expect(response.status()).toBe(200);

    await expect(page).toHaveURL(
      /indicadores\/infraestrutura\/analise-temporal/
    );

    await expect(page.locator('app-root')).toBeVisible();
  });


  test('QA07-02 - Deve selecionar e limpar uma escola', async ({ page }) => {
    await page.goto('/indicadores/infraestrutura/analise-temporal');

    const respostaApi = page.waitForResponse(response =>
      response.url().includes('/comparacao-municipio') &&
      response.status() === 200
    );

    await page.locator('#pn_id_6')
      .getByRole('button', { name: 'dropdown trigger' })
      .click();

    await page.getByRole('option')
      .filter({ hasText: '15159485' })
      .click();

    const response = await respostaApi;
    const dados = await response.json();

    expect(dados.data.escola.co_entidade).toBe(15159485);
    expect(dados.data.escola.no_entidade).toContain('ACADEMIA BORDONI');

    const composicao = page.getByRole('region', {
      name: /Composição do índice/
    });

    await expect(composicao).toBeVisible();

    await composicao.getByLabel('dropdown trigger').click();
    await page.getByRole('option', { name: '2024' }).click();

    await expect(composicao).toContainText('2024');

    const registro2024 = dados.data.serie.find(item => item.ano === 2024);

    expect(registro2024).toBeDefined();
    expect(registro2024.situacao).toBe('disponivel');
    expect(registro2024.registro_historico_disponivel).toBe(true);
    expect(registro2024.indice_escola_percentual).toBeDefined();
    expect(registro2024.media_municipal_percentual).toBeDefined();

    await page.locator('#pn_id_6')
      .getByRole('button', { name: 'Limpar seleção' })
      .click();

    await expect(page.locator('#pn_id_6'))
      .not.toContainText('15159485');

    await expect(page.locator('body'))
      .toContainText('Selecione uma escola para visualizar a evolução temporal.');

    await expect(page.locator('body'))
      .toContainText('Selecione uma escola para visualizar a composição do índice.');

    await expect(page.locator('body'))
      .toContainText('Escola selecionada');

    await expect(page.locator('body'))
      .toContainText('Sem dados');
  });


  test('QA07-03 - Deve exibir os 17 indicadores conforme os dados da API', async ({ page }) => {
    await page.goto('/indicadores/infraestrutura/analise-temporal');

    const respostaApi = page.waitForResponse(response =>
      response.url().includes('/comparacao-municipio') &&
      response.status() === 200
    );

    await page.locator('#pn_id_6')
      .getByRole('button', { name: 'dropdown trigger' })
      .click();

    await page.getByRole('option')
      .filter({ hasText: '15159485' })
      .click();

    const response = await respostaApi;
    const dados = await response.json();

    const registro2024 = dados.data.serie.find(item => item.ano === 2024);

    expect(registro2024).toBeDefined();
    expect(registro2024.composicao_escola).toBeDefined();

    const composicao = page.getByRole('region', {
      name: /Composição do índice/
    });

    await expect(composicao).toBeVisible();

    await composicao.getByLabel('dropdown trigger').click();
    await page.getByRole('option', { name: '2024' }).click();

    const indicadores = [
      ['Água potável', 'in_agua_potavel'],
      ['Energia (rede pública)', 'in_energia_rede_publica'],
      ['Esgoto (rede pública)', 'in_esgoto_rede_publica'],
      ['Coleta de lixo', 'in_lixo_servico_coleta'],
      ['Banheiro', 'in_banheiro'],
      ['Banheiro acessível (PNE)', 'in_banheiro_pne'],
      ['Biblioteca', 'in_biblioteca'],
      ['Sala de leitura', 'in_sala_leitura'],
      ['Laboratório de ciências', 'in_laboratorio_ciencias'],
      ['Laboratório de informática', 'in_laboratorio_informatica'],
      ['Sala multiuso', 'in_sala_multiuso'],
      ['Sala de atendimento especial', 'in_sala_atendimento_especial'],
      ['Cozinha', 'in_cozinha'],
      ['Refeitório', 'in_refeitorio'],
      ['Quadra de esportes', 'in_quadra_esportes'],
      ['Pátio coberto', 'in_patio_coberto'],
      ['Auditório', 'in_auditorio']
    ];

    const textoExibido = await composicao.innerText();

    for (const [rotulo, campo] of indicadores) {
      const valorApi = registro2024.composicao_escola[campo];
      const valorEsperado = valorApi === 1 ? 'Sim' : 'Não';

      expect([0, 1]).toContain(valorApi);

      expect(
        textoExibido,
        `O indicador "${rotulo}" deveria apresentar o valor "${valorEsperado}".`
      ).toContain(`${rotulo}\n${valorEsperado}`);
    }

    const resumoEsperado =
      `${registro2024.quantidade_indicadores_presentes} de ` +
      `${registro2024.quantidade_indicadores_validos} indicadores válidos presentes ` +
      `(${registro2024.total_indicadores} no total).`;

    expect(textoExibido).toContain(resumoEsperado);
  });


  test('QA07-08 - Deve exibir legenda e tooltip com dados do gráfico', async ({ page }) => {
    await page.goto('/indicadores/infraestrutura/analise-temporal');

    const respostaApi = page.waitForResponse(response =>
      response.url().includes('/comparacao-municipio') &&
      response.status() === 200
    );

    await page.locator('#pn_id_6')
      .getByRole('button', { name: 'dropdown trigger' })
      .click();

    await page.getByRole('option')
      .filter({ hasText: '15159485' })
      .click();

    const response = await respostaApi;
    const dados = await response.json();

    const registro2022 = dados.data.serie.find(item => item.ano === 2022);

    expect(registro2022).toBeDefined();

    const grafico = page.locator('.js-plotly-plot');

    await expect(grafico).toBeVisible();

    const textosGrafico = await grafico.locator('svg text').allTextContents();

    expect(textosGrafico).toContain('Escola selecionada');
    expect(textosGrafico).toContain('Média das demais escolas do município');

    const ponto = grafico.locator('.scatterlayer .point').first();

    await expect(ponto).toBeVisible();

    const caixa = await ponto.boundingBox();

    expect(caixa).not.toBeNull();

    await page.mouse.move(
      caixa.x + caixa.width / 2,
      caixa.y + caixa.height / 2
    );

    const tooltip = grafico.locator('.hoverlayer');

    await expect(tooltip).toBeVisible();

    const textoTooltip = await tooltip.textContent();

    expect(textoTooltip).toContain('2022');
    expect(textoTooltip).toContain('Escola selecionada');
    expect(textoTooltip).toContain('Demais escolas do município');
    expect(textoTooltip).toContain('Diferença');
  });




test('QA07-09 - Deve informar falha na requisição e permitir nova tentativa', async ({ page }) => {
  let quantidadeRequisicoes = 0;

  await page.route('**/comparacao-municipio', async route => {
    quantidadeRequisicoes++;

    if (quantidadeRequisicoes === 1) {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Erro interno do servidor'
        })
      });
    } else {
      await route.continue();
    }
  });

  await page.goto('/indicadores/infraestrutura/analise-temporal');

  await page.locator('#pn_id_6')
    .getByRole('button', { name: 'dropdown trigger' })
    .click();

  await page.getByRole('option')
    .filter({ hasText: '15159485' })
    .click();

  await expect(page.locator('body'))
    .toContainText('Falha na requisição. Por favor, tente novamente.');

  const tentarNovamente = page.getByRole('button', {
    name: /Tentar novamente/i
  });

  await expect(tentarNovamente).toBeVisible();

  await tentarNovamente.click();

  await expect.poll(() => quantidadeRequisicoes).toBeGreaterThan(1);

  await expect(page.locator('body'))
    .not.toContainText('Falha na requisição. Por favor, tente novamente.');
});


});
