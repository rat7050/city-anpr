import ReactECharts from 'echarts-for-react';
import { useMemo } from 'react';

interface TrafficChartProps {
  type: 'bar' | 'line' | 'pie' | 'heatmap';
  data: any;
  title?: string;
  height?: string;
}

export default function TrafficChart({ type, data, title, height = '300px' }: TrafficChartProps) {
  const options = useMemo(() => {
    const baseOpt = {
      backgroundColor: 'transparent',
      textStyle: { color: '#94a3b8' },
      title: title ? { text: title, textStyle: { color: '#f1f5f9', fontSize: 16 } } : undefined,
      tooltip: { trigger: type === 'pie' ? 'item' : 'axis', backgroundColor: '#1e293b', borderColor: '#334155', textStyle: { color: '#f1f5f9' } },
    };

    if (type === 'line' || type === 'bar') {
      return {
        ...baseOpt,
        xAxis: { type: 'category', data: data.labels, axisLine: { lineStyle: { color: '#475569' } } },
        yAxis: { type: 'value', splitLine: { lineStyle: { color: '#334155', type: 'dashed' } } },
        series: data.datasets.map((ds: any) => ({
          name: ds.label,
          type: type,
          data: ds.data,
          smooth: true,
          itemStyle: { color: ds.color || '#3b82f6' },
          areaStyle: type === 'line' ? { color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: ds.color || '#3b82f6' }, { offset: 1, color: 'transparent' }]
          }, opacity: 0.2 } : undefined
        })),
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true }
      };
    }

    if (type === 'pie') {
      return {
        ...baseOpt,
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          itemStyle: { borderRadius: 10, borderColor: '#1e293b', borderWidth: 2 },
          label: { color: '#cbd5e1' },
          data: data
        }]
      };
    }
    return baseOpt;
  }, [type, data, title]);

  return <ReactECharts option={options} style={{ height, width: '100%' }} />;
}
