// src/features/intake/components/IntakeOrderDetailDrawer.jsx
import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { updateIntakeOrder } from '../services/intakeOrders';

const fieldDefs = [
  { name: 'customer_name', label: 'Cliente', type: 'text' },
  { name: 'locality', label: 'Localidad', type: 'text' },
  { name: 'carrier', label: 'Carrier', type: 'text' },
  { name: 'carrier_redespacho', label: 'Redespacho', type: 'text' },
  { name: 'order_number', label: 'Orden #', type: 'text', disabled: true },
  { name: 'notes', label: 'Notas', type: 'textarea' },
  { name: 'declared_value', label: 'Valor Declarado', type: 'number', step: '0.01' },
];

const flowStatusOptions = [
  { value: 'new', label: 'New' },
  { value: 'parsed', label: 'Parsed' },
  { value: 'validated', label: 'Validated' },
  { value: 'assigned', label: 'Assigned' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
  { value: 'error', label: 'Error' },
];

const IntakeOrderDetailDrawer = ({ open, onClose, order, onSaved }) => {
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({});
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (order) {
      const initial = {};
      for (const f of fieldDefs) initial[f.name] = order[f.name] ?? '';
      initial.flow_status = order.flow_status;
      setForm(initial);
      setEditing(false);
      setDirty(false);
      setError(null);
      setSaving(false);
    }
  }, [order]);

  const handleChange = (name, value) => {
    setForm(prev => ({ ...prev, [name]: value }));
    setDirty(true);
  };

  const handleCancelEdit = () => {
    if (!order) return;
    const reset = {};
    for (const f of fieldDefs) reset[f.name] = order[f.name] ?? '';
    reset.flow_status = order.flow_status;
    setForm(reset);
    setEditing(false);
    setDirty(false);
    setError(null);
  };

  const handleSave = useCallback(async () => {
    if (!order || !dirty) { setEditing(false); return; }
    setSaving(true);
    setError(null);
    try {
      const payload = {};
      for (const f of fieldDefs) {
        if (form[f.name] !== order[f.name]) payload[f.name] = form[f.name];
      }
      if (form.flow_status !== order.flow_status) payload.flow_status = form.flow_status;
      if (Object.keys(payload).length === 0) {
        setEditing(false);
        setDirty(false);
        return;
      }
      const updated = await updateIntakeOrder(order.id, payload);
      onSaved && onSaved(updated);
      setEditing(false);
      setDirty(false);
    } catch (e) {
      console.error('Error guardando intake order', e);
      setError(e.response?.data?.detail || e.message || 'Error al guardar');
    } finally {
      setSaving(false);
    }
  }, [order, dirty, form, onSaved]);

  if (!open || !order) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/40" onClick={onClose} />
      <div className="w-full max-w-xl bg-white dark:bg-surface-800 shadow-xl h-full overflow-y-auto p-6 flex flex-col gap-4">
        <div className="flex items-start justify-between">
          <h2 className="text-lg font-semibold">Nota de Pedido #{order.order_number || order.id}</h2>
          <div className="flex gap-2">
            {!editing && (
              <button onClick={() => setEditing(true)} className="btn btn-xs bg-amber-500 hover:bg-amber-600 text-white">Editar</button>
            )}
            {editing && (
              <>
                <button onClick={handleCancelEdit} className="btn btn-xs bg-surface-300 hover:bg-surface-400 text-text-primary">Cancelar</button>
                <button disabled={saving} onClick={handleSave} className="btn btn-xs bg-primary-600 hover:bg-primary-700 text-white disabled:opacity-60">{saving ? 'Guardando…' : 'Guardar'}</button>
              </>
            )}
            <button onClick={onClose} className="btn btn-xs bg-error-600 hover:bg-error-700 text-white">Cerrar</button>
          </div>
        </div>
        {error && <div className="text-xs text-error-600">{error}</div>}
        <section className="space-y-3 text-sm">
          {fieldDefs.map(f => (
            <div key={f.name} className="flex flex-col gap-1">
              <label className="text-xs font-semibold uppercase tracking-wide">{f.label}</label>
              {f.type === 'textarea' ? (
                <textarea
                  disabled={!editing || f.disabled}
                  className="border rounded p-2 text-sm bg-white dark:bg-surface-700 disabled:opacity-60"
                  rows={3}
                  value={form[f.name]}
                  onChange={(e) => handleChange(f.name, e.target.value)}
                />
              ) : (
                <input
                  type={f.type}
                  step={f.step}
                  disabled={!editing || f.disabled}
                  className="border rounded p-2 text-sm bg-white dark:bg-surface-700 disabled:opacity-60"
                  value={form[f.name]}
                  onChange={(e) => handleChange(f.name, e.target.value)}
                />
              )}
            </div>
          ))}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold uppercase tracking-wide">Estado flujo</label>
            <select
              disabled={!editing}
              className="border rounded p-2 text-sm bg-white dark:bg-surface-700 disabled:opacity-60"
              value={form.flow_status}
              onChange={(e) => handleChange('flow_status', e.target.value)}
            >
              {flowStatusOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
        </section>
        <section>
          <h3 className="font-semibold mb-2">Ítems</h3>
          <div className="border border-border-primary rounded-md max-h-64 overflow-auto">
            <table className="w-full text-xs">
              <thead className="bg-surface-200 sticky top-0">
                <tr>
                  <th className="px-2 py-1 text-left">#</th>
                  <th className="px-2 py-1 text-left">Código</th>
                  <th className="px-2 py-1 text-left">Descripción</th>
                  <th className="px-2 py-1 text-right">Qty</th>
                  <th className="px-2 py-1 text-left">Match</th>
                </tr>
              </thead>
              <tbody>
                {(order.items || []).map(it => (
                  <tr key={it.id} className="border-t border-border-subtle">
                    <td className="px-2 py-1 whitespace-nowrap">{it.line_no}</td>
                    <td className="px-2 py-1 whitespace-nowrap">{it.code || '—'}</td>
                    <td className="px-2 py-1 max-w-[200px] truncate" title={it.raw_description}>{it.raw_description || '—'}</td>
                    <td className="px-2 py-1 text-right">{it.qty}</td>
                    <td className="px-2 py-1 whitespace-nowrap">{it.match_method || it.confidence ? `${it.match_method || ''} (${it.match_confidence || it.confidence || '—'})` : '—'}</td>
                  </tr>
                ))}
                {(!order.items || order.items.length === 0) && (
                  <tr><td colSpan={5} className="px-2 py-4 text-center text-text-secondary">Sin ítems</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
        <section>
            <h3 className="font-semibold mb-2">Payload (raw)</h3>
            <pre className="text-[10px] bg-surface-100 p-2 rounded overflow-auto max-h-52">{JSON.stringify(order.payload, null, 2)}</pre>
        </section>
      </div>
    </div>
  );
};

IntakeOrderDetailDrawer.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  order: PropTypes.object,
  onSaved: PropTypes.func,
};

export default IntakeOrderDetailDrawer;
