import React, { useState, useCallback, useMemo } from 'react';
import AssignedUserSelect from './AssignedUserSelect';
import { ingestIntakeOrder } from '../services/intakeIngest';

// Wizard multi-paso: Datos -> Items -> Revisión
// Props: open, onClose, onCreated(orderSummary)
const CreateIntakeOrderWizard = ({ open, onClose, onCreated }) => {
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [createdInfo, setCreatedInfo] = useState(null);

  const [form, setForm] = useState({
    customer_name: '', locality: '', carrier: '', carrier_redespacho: '', order_number: '', declared_value: '', notes: '', assigned_to: ''
  });
  const [items, setItems] = useState([{ line_no: 1, qty: 1, code: '', raw_description: '' }]);
  const [userCache, setUserCache] = useState([]);

  const canNextFromDatos = form.customer_name.trim() && form.assigned_to; // assigned_to obligatorio
  const hasDuplicateLines = useMemo(() => {
    const lines = items.map(i => i.line_no);
    const set = new Set(lines);
    return set.size !== lines.length;
  }, [items]);
  const canNextFromItems = items.length > 0 && !hasDuplicateLines && items.every(it => it.qty > 0 && (it.code.trim() || it.raw_description.trim()));

  const addItem = () => {
    setItems(prev => {
      const nextLine = (prev[prev.length - 1]?.line_no || prev.length) + 1;
      return [...prev, { line_no: nextLine, qty: 1, code: '', raw_description: '' }];
    });
  };
  const updateItem = (idx, patch) => {
    setItems(prev => prev.map((it, i) => i === idx ? { ...it, ...patch } : it));
  };
  const removeItem = (idx) => {
    setItems(prev => prev.filter((_, i) => i !== idx));
  };

  const duplicateItem = (idx) => {
    setItems(prev => {
      const base = prev[idx];
      const nextLine = (prev[prev.length - 1]?.line_no || prev.length) + 1;
      return [...prev, { ...base, line_no: nextLine }];
    });
  };

  const warnings = useMemo(() => {
    const list = [];
    if (items.length > 200) list.push('Demasiados ítems (>200) puede afectar rendimiento.');
    const empties = items.filter(i => !i.code.trim() && !i.raw_description.trim()).length;
    if (empties) list.push(`${empties} ítems sin código ni descripción.`);
    if (hasDuplicateLines) list.push('Hay números de línea duplicados.');
    return list;
  }, [items, hasDuplicateLines]);

  const handleSubmit = useCallback(async () => {
    setSubmitting(true); setError(null);
    try {
      // construir payload ingest
      const todayYmd = new Date().toISOString().slice(0,10).replace(/-/g,'');
      const conversation_id = `manual-${todayYmd}`; // agrupar por día
      const raw_text_merged = items.map(i => (i.raw_description || i.code)).join('\n');
      const payload = {
        source: 'manual',
        conversation_id,
        order: {
          order_number: form.order_number || undefined,
          declared_value: form.declared_value || undefined,
          notes: form.notes || undefined,
        },
        customer: {
          name: form.customer_name || undefined,
          locality: form.locality || undefined,
          address: {},
        },
        shipping: {
          carrier: form.carrier || undefined,
          redespacho: form.carrier_redespacho || undefined,
        },
        items: items.map(i => ({
          line_no: i.line_no,
          qty: Number(i.qty) || 0,
          code: i.code || undefined,
          raw_description: i.raw_description || undefined,
        })),
        assignment: { assigned_to: form.assigned_to },
        raw_text_merged,
        payload: { manual: true }
      };
      const res = await ingestIntakeOrder(payload);
      if (res.status !== 'SUCCESS') throw new Error(res.message || 'Fallo ingest');
      const orderId = res.data.order_id;
      setCreatedInfo({ ...res.data, assigned_to: form.assigned_to });
      setStep(4);
      // Notificamos al padre: solo id y algunos campos base que necesitamos para prepend
      const userObj = userCache.find(u => String(u.id) === String(form.assigned_to));
      const assigned_to_name = userObj ? (`${userObj.first_name ?? ''} ${userObj.last_name ?? ''}`.trim() || userObj.username || userObj.email) : null;
      onCreated?.({ id: orderId, customer_name: form.customer_name, order_number: form.order_number, flow_status: 'assigned', items_count: items.length, carrier: form.carrier, notes: form.notes, assigned_to_id: form.assigned_to, assigned_to_name });
    } catch (e) {
      setError(e.message || 'Error inesperado');
    } finally {
      setSubmitting(false);
    }
  }, [form, items, onCreated, userCache]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[10000] flex">
      <div className="flex-1 bg-black/30" onClick={() => !submitting && onClose?.()} />
      <div className="w-full max-w-4xl bg-white h-full shadow-xl flex flex-col">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold">Crear Nota de Pedido</h2>
          <button onClick={() => !submitting && onClose?.()} className="text-sm text-text-secondary hover:text-text-primary">Cerrar</button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {step === 1 && (
            <div>
              <h3 className="font-medium mb-4">Datos generales</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">Cliente *</label>
                  <input value={form.customer_name} onChange={e=>setForm(f=>({...f, customer_name:e.target.value}))} className="mt-1 w-full border rounded px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Localidad</label>
                  <input value={form.locality} onChange={e=>setForm(f=>({...f, locality:e.target.value}))} className="mt-1 w-full border rounded px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Transporte</label>
                  <input value={form.carrier} onChange={e=>setForm(f=>({...f, carrier:e.target.value}))} className="mt-1 w-full border rounded px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Redespacho</label>
                  <input value={form.carrier_redespacho} onChange={e=>setForm(f=>({...f, carrier_redespacho:e.target.value}))} className="mt-1 w-full border rounded px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium">N° Pedido</label>
                  <input value={form.order_number} onChange={e=>setForm(f=>({...f, order_number:e.target.value}))} className="mt-1 w-full border rounded px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Valor declarado</label>
                  <input type="number" value={form.declared_value} onChange={e=>setForm(f=>({...f, declared_value:e.target.value}))} className="mt-1 w-full border rounded px-3 py-2 text-sm" />
                </div>
                <div className="md:col-span-2">
                  <AssignedUserSelect required value={form.assigned_to} onChange={(v)=>setForm(f=>({...f, assigned_to:v}))} onUsersLoaded={(users)=>setUserCache(users)} />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium">Notas</label>
                  <textarea rows={3} value={form.notes} onChange={e=>setForm(f=>({...f, notes:e.target.value}))} className="mt-1 w-full border rounded px-3 py-2 text-sm" />
                </div>
              </div>
            </div>
          )}
          {step === 2 && (
            <div>
              <h3 className="font-medium mb-4">Ítems</h3>
              <table className="w-full text-sm border">
                <thead className="bg-background-100">
                  <tr>
                    <th className="p-2 border">Línea</th>
                    <th className="p-2 border">Cantidad</th>
                    <th className="p-2 border">Código</th>
                    <th className="p-2 border">Descripción</th>
                    <th className="p-2 border w-20">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((it, idx) => {
                    const invalid = !(it.code.trim() || it.raw_description.trim()) || !(Number(it.qty) > 0);
                    return (
                      <tr key={idx} className={invalid ? 'bg-red-50' : ''}>
                        <td className="p-1 border">
                          <input type="number" value={it.line_no} onChange={e=>updateItem(idx,{ line_no:Number(e.target.value)||1 })} className="w-20 border rounded px-1 py-1 text-sm" />
                        </td>
                        <td className="p-1 border">
                          <input type="number" step="0.01" value={it.qty} onChange={e=>updateItem(idx,{ qty:e.target.value })} className="w-24 border rounded px-1 py-1 text-sm" />
                        </td>
                        <td className="p-1 border">
                          <input value={it.code} onChange={e=>updateItem(idx,{ code:e.target.value })} className="w-full border rounded px-1 py-1" />
                        </td>
                        <td className="p-1 border">
                          <input value={it.raw_description} onChange={e=>updateItem(idx,{ raw_description:e.target.value })} className="w-full border rounded px-1 py-1" />
                        </td>
                        <td className="p-1 border text-center space-x-1">
                          <button type="button" onClick={()=>duplicateItem(idx)} className="px-1 py-0.5 text-xs rounded bg-primary-100 hover:bg-primary-200">Dup</button>
                          <button type="button" onClick={()=>removeItem(idx)} disabled={items.length===1} className="px-1 py-0.5 text-xs rounded bg-error-100 hover:bg-error-200 disabled:opacity-40">Del</button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              <div className="mt-3 flex justify-between">
                <button type="button" onClick={addItem} className="px-3 py-1.5 text-sm rounded bg-primary-600 text-white hover:bg-primary-700">+ Ítem</button>
                <div className="text-xs text-text-secondary">{items.length} ítems</div>
              </div>
            </div>
          )}
          {step === 3 && (
            <div>
              <h3 className="font-medium mb-4">Revisión</h3>
              <ul className="text-sm mb-4">
                <li><strong>Cliente:</strong> {form.customer_name}</li>
                <li><strong>Asignado a:</strong> {form.assigned_to}</li>
                <li><strong>Ítems:</strong> {items.length}</li>
                {form.order_number && <li><strong>N° Pedido:</strong> {form.order_number}</li>}
              </ul>
              {warnings.length > 0 && (
                <div className="mb-4 p-3 border border-amber-300 bg-amber-50 rounded text-xs space-y-1">
                  {warnings.map((w,i)=>(<div key={i}>• {w}</div>))}
                </div>
              )}
              <p className="text-xs text-text-secondary mb-2">Al confirmar se ejecutará el matching automático y se crearán Cutting Orders para productos con subproductos (si aplica).</p>
              {error && <div className="mb-2 text-error-600 text-sm">Error: {error}</div>}
            </div>
          )}
          {step === 4 && (
            <div>
              <h3 className="font-medium mb-3">Creación completada</h3>
              {createdInfo && (
                <div className="text-sm space-y-1">
                  <div>Orden ID: {createdInfo.order_id}</div>
                  <div>Items creados: {createdInfo.items_created}</div>
                  <div>Cutting generadas: {createdInfo.cutting_orders_created}</div>
                  <div>Estado: {createdInfo.flow_status}</div>
                </div>
              )}
              <div className="mt-4">
                <button onClick={()=>onClose?.()} className="px-4 py-2 bg-primary-600 text-white rounded text-sm hover:bg-primary-700">Cerrar</button>
              </div>
            </div>
          )}
        </div>
        {step < 4 && (
          <div className="p-4 border-t flex items-center justify-between">
            <div className="space-x-2">
              {step > 1 && <button disabled={submitting} onClick={()=>setStep(s=>s-1)} className="px-3 py-1.5 text-sm rounded border hover:bg-background-100">Atrás</button>}
            </div>
            <div className="space-x-2">
              {step === 1 && <button disabled={!canNextFromDatos || submitting} onClick={()=>setStep(2)} className="px-4 py-1.5 text-sm rounded bg-primary-600 text-white disabled:opacity-50">Siguiente</button>}
              {step === 2 && <button disabled={!canNextFromItems || submitting} onClick={()=>setStep(3)} className="px-4 py-1.5 text-sm rounded bg-primary-600 text-white disabled:opacity-50">Revisión</button>}
              {step === 3 && <button disabled={submitting} onClick={handleSubmit} className="px-4 py-1.5 text-sm rounded bg-green-600 text-white disabled:opacity-50">Confirmar & Crear</button>}
            </div>
          </div>
        )}
        {submitting && step !==4 && (
          <div className="absolute inset-0 bg-white/70 flex items-center justify-center text-sm">
            Procesando...
          </div>
        )}
      </div>
    </div>
  );
};

export default CreateIntakeOrderWizard;
