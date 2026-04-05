import { WellDesignInline } from '@/components/wells/WellIdWithDesign';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableRow } from '@/components/ui/table';
import { OdCurveChart } from '@/components/charts/OdCurveChart';
import { useWellTimeseries } from '@/api/client';
import { designParamEntries } from '@/lib/wellDesign';
import type { WellResult } from '@/types';

interface Props {
  well: WellResult;
  iterationId: string;
  onClose: () => void;
}

export function WellDetailPanel({ well, iterationId, onClose }: Props) {
  const { data: timeseries, isLoading } = useWellTimeseries(iterationId, well.well);

  return (
    <div className="w-96 shrink-0 space-y-4 overflow-y-auto">
      <div className="flex items-center justify-between gap-2">
        <div className="min-w-0">
          <h3 className="text-lg font-semibold">Well {well.well}</h3>
          <WellDesignInline params={well.params} className="mt-1 block text-sm" />
        </div>
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground text-sm px-2 py-1 rounded hover:bg-muted transition-colors"
        >
          Close
        </button>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Growth Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableBody>
              <TableRow>
                <TableCell className="text-muted-foreground">Growth Rate</TableCell>
                <TableCell className="text-right font-mono">{well.growth_rate.toFixed(4)} /h</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="text-muted-foreground">Doubling Time</TableCell>
                <TableCell className="text-right font-mono">
                  {well.doubling_time_hours !== null ? `${well.doubling_time_hours.toFixed(1)} h` : 'N/A'}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="text-muted-foreground">R-squared</TableCell>
                <TableCell className="text-right font-mono">{well.r_squared.toFixed(4)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="text-muted-foreground">Max OD</TableCell>
                <TableCell className="text-right font-mono">{well.max_od.toFixed(4)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="text-muted-foreground">Data Points</TableCell>
                <TableCell className="text-right font-mono">{well.n_datapoints}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="text-muted-foreground">Parent Well</TableCell>
                <TableCell className="text-right font-mono">{well.parent_well}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Design Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableBody>
              {designParamEntries(well.params).map(({ key, label, display }) => (
                <TableRow key={key}>
                  <TableCell className="text-muted-foreground">{label}</TableCell>
                  <TableCell className="text-right font-mono">{display}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">OD Curve</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : (
            <OdCurveChart data={timeseries ?? []} well={well.well} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
