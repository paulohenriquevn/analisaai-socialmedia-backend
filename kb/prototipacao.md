# 🧩 Prototipação Inicial de Componentes – *Analisa.ai Social Media*

Analisa.ai Social Media é uma plataforma de análise de redes sociais que utiliza IA para avaliar influenciadores. O sistema precisa ser escalável, seguro e integrável com APIs de redes sociais (Instagram, TikTok, Facebook), além de processar grandes volumes de dados em tempo quase real.

Além disso, o backend deve ser capaz de considerar as características do público-alvo de cada influenciador, como faixa etária, interesses, localização e perfil de consumo. Isso garantirá que os insights gerados sejam contextualizados e mais relevantes para os objetivos de marketing e comunicação das marcas que utilizam a plataforma.

---

## 📊 Épico 1 – Dashboard de Métricas Básicas

### 🔹 `<MetricCard>`
> Exibe KPIs como Engajamento, Alcance, Crescimento.

**Props**:
- `title: string` – Nome da métrica (ex: “Engajamento”)
- `value: string | number` – Valor da métrica (ex: “8,5%”)
- `icon?: string` – Ícone opcional
- `color?: string` – Cor de destaque (variação por métrica)

**Eventos**:
- `onClick` – Abre visualização detalhada

**Slots**:
- `tooltip` – Detalhes adicionais ao passar o mouse

---

### 🔹 `<DatePlatformFilter>`
> Componente para aplicar filtros por período e plataforma.

**Props**:
- `initialDateRange: [Date, Date]`
- `platforms: string[]` – Ex: ["Instagram", "TikTok"]
- `selectedPlatform: string`

**Eventos**:
- `onFilterChange({startDate, endDate, platform})`

**Comportamento**:
- Usa `<DatePicker>` + `<Select>` combinados

---

### 🔹 `<PerformanceChart>`
> Gráfico de linha para visualização de crescimento.

**Props**:
- `series: ChartSeries[]`
- `xAxisLabels: string[]`
- `highlightPeaks?: boolean`

**Eventos**:
- `onPointClick(dataPoint)`

**Tecnologia**:
- Usa `apexcharts-angular`, com zoom e tooltips

---

## 💬 Épico 2 – Análise de Sentimentos

### 🔹 `<SentimentPieChart>`
> Gráfico de pizza mostrando distribuição de sentimentos.

**Props**:
- `data: { positive: number, neutral: number, negative: number }`

**Eventos**:
- `onSliceClick(type: 'positive' | 'neutral' | 'negative')`

**Slots**:
- `tooltipContent` – Customização do tooltip

---

### 🔹 `<CommentList>`
> Lista de comentários com destaque semântico.

**Props**:
- `comments: CommentItem[]`  
  ```ts
  type CommentItem = {
    text: string;
    sentiment: 'positive' | 'neutral' | 'negative';
    keywords?: string[];
  }
  ```

**Comportamento**:
- Destaque automático de palavras-chave
- Suporte a emojis

---

## 📈 Épico 3 – Benchmarking

### 🔹 `<BenchmarkChart>`
> Gráfico de barras para comparar perfis.

**Props**:
- `profiles: string[]`
- `metrics: { [profileName: string]: number[] }`
- `metricNames: string[]`

**Eventos**:
- `onBarClick(profile, metric)`

---

### 🔹 `<SavedComparisonSelector>`
> Componente para salvar e recuperar comparações.

**Props**:
- `savedComparisons: { name: string, profiles: string[] }[]`

**Eventos**:
- `onSave(name: string)`
- `onSelect(name: string)`

---

## 📄 Épico 4 – Relatórios

### 🔹 `<ReportCustomizer>`
> Checkboxes para seleção de seções no relatório.

**Props**:
- `sections: { id: string, name: string, selected: boolean }[]`

**Eventos**:
- `onSectionToggle(id: string, selected: boolean)`

---

### 🔹 `<ReportPreview>`
> Pré-visualização do relatório com identidade visual.

**Props**:
- `logoUrl: string`
- `primaryColor: string`
- `selectedSections: string[]`

**Slots**:
- `customFooter` – Assinatura opcional

---

## ♿ Épico 5 – Acessibilidade e Responsividade

### 🔹 `<AccessibleChartWrapper>`
> Wrapper para gráficos com suporte a teclado e leitores.

**Props**:
- `title: string`
- `chartComponent: Component`

**Comportamento**:
- Usa `aria-label`, `tabindex`, tooltips acessíveis

---

### 🔹 `<ResponsiveLayout>`
> Layout que adapta cards e gráficos para dispositivos mobile.

**Props**:
- `breakpoints?: { sm: number, md: number, lg: number }`
- `orientation?: 'vertical' | 'horizontal'`

**Slots**:
- `default` – Conteúdo principal responsivo

---

## ✅ Repositório Storybook (sugestão de estrutura)
```
📁 stories/
├── MetricCard.stories.ts
├── PerformanceChart.stories.ts
├── CommentList.stories.ts
├── BenchmarkChart.stories.ts
├── ReportCustomizer.stories.ts
├── ResponsiveLayout.stories.ts
```

---

## 📁 `stories/BenchmarkChart.stories.ts`

```ts
import { Meta, Story } from '@storybook/angular';
import { BenchmarkChartComponent } from '../src/app/components/benchmark-chart/benchmark-chart.component';

export default {
  title: 'Benchmarking/BenchmarkChart',
  component: BenchmarkChartComponent,
} as Meta;

const Template: Story<BenchmarkChartComponent> = (args: BenchmarkChartComponent) => ({
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  profiles: ['@joana', '@marcos', '@influencerX'],
  metrics: {
    '@joana': [8.5, 1.2, 3.4],
    '@marcos': [7.1, 1.0, 2.9],
    '@influencerX': [9.3, 1.4, 4.2],
  },
  metricNames: ['Engajamento (%)', 'Alcance (M)', 'Crescimento (%)'],
};
```

---

## 📁 `stories/SavedComparisonSelector.stories.ts`

```ts
import { Meta, Story } from '@storybook/angular';
import { SavedComparisonSelectorComponent } from '../src/app/components/saved-comparison-selector/saved-comparison-selector.component';

export default {
  title: 'Benchmarking/SavedComparisonSelector',
  component: SavedComparisonSelectorComponent,
} as Meta;

const Template: Story<SavedComparisonSelectorComponent> = (args: SavedComparisonSelectorComponent) => ({
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  savedComparisons: [
    { name: 'Campanha Verão', profiles: ['@joana', '@marcos'] },
    { name: 'Comparativo Julho', profiles: ['@joao', '@influencerX'] }
  ],
};
```

---

## 📁 `stories/ReportCustomizer.stories.ts`

```ts
import { Meta, Story } from '@storybook/angular';
import { ReportCustomizerComponent } from '../src/app/components/report-customizer/report-customizer.component';

export default {
  title: 'Relatórios/ReportCustomizer',
  component: ReportCustomizerComponent,
} as Meta;

const Template: Story<ReportCustomizerComponent> = (args: ReportCustomizerComponent) => ({
  props: args,
});

export const Checklist = Template.bind({});
Checklist.args = {
  sections: [
    { id: 'engagement', name: 'Engajamento', selected: true },
    { id: 'reach', name: 'Alcance', selected: false },
    { id: 'sentiment', name: 'Sentimentos', selected: true },
  ]
};
```

---

## 📁 `stories/ReportPreview.stories.ts`

```ts
import { Meta, Story } from '@storybook/angular';
import { ReportPreviewComponent } from '../src/app/components/report-preview/report-preview.component';

export default {
  title: 'Relatórios/ReportPreview',
  component: ReportPreviewComponent,
} as Meta;

const Template: Story<ReportPreviewComponent> = (args: ReportPreviewComponent) => ({
  props: args,
});

export const CustomVisual = Template.bind({});
CustomVisual.args = {
  logoUrl: 'https://example.com/logo.png',
  primaryColor: '#6D28D9',
  selectedSections: ['engagement', 'sentiment'],
};
```

---

## 📁 `stories/AccessibleChartWrapper.stories.ts`

```ts
import { Meta, Story } from '@storybook/angular';
import { AccessibleChartWrapperComponent } from '../src/app/components/accessible-chart-wrapper/accessible-chart-wrapper.component';

export default {
  title: 'Acessibilidade/AccessibleChartWrapper',
  component: AccessibleChartWrapperComponent,
} as Meta;

const Template: Story<AccessibleChartWrapperComponent> = (args: AccessibleChartWrapperComponent) => ({
  props: args,
});

export const AccessibleChart = Template.bind({});
AccessibleChart.args = {
  title: 'Desempenho de Engajamento',
  // O `chartComponent` será injetado via ng-content no wrapper real.
};
```

---

## 📁 `stories/ResponsiveLayout.stories.ts`

```ts
import { Meta, Story } from '@storybook/angular';
import { ResponsiveLayoutComponent } from '../src/app/components/responsive-layout/responsive-layout.component';

export default {
  title: 'Acessibilidade/ResponsiveLayout',
  component: ResponsiveLayoutComponent,
} as Meta;

const Template: Story<ResponsiveLayoutComponent> = (args: ResponsiveLayoutComponent) => ({
  props: args,
  template: `
    <app-responsive-layout>
      <div class="p-4 bg-gray-100">Componente 1</div>
      <div class="p-4 bg-gray-200">Componente 2</div>
    </app-responsive-layout>
  `
});

export const GridMobileFirst = Template.bind({});
GridMobileFirst.args = {
  breakpoints: { sm: 320, md: 768, lg: 1024 },
  orientation: 'vertical',
};
```
---

