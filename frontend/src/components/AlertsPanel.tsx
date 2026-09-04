'use client';

import { useState, useEffect } from 'react';
import {
  Bell, Plus, Trash2, Pause, Play, X, AlertTriangle,
  TrendingUp, TrendingDown, Percent, Activity, Newspaper
} from 'lucide-react';
import {
  Alert, AlertCreate, AlertTemplate, AlertType,
  getAlerts, createAlert, deleteAlert, pauseAlert, resumeAlert, getAlertTemplates, checkAlerts
} from '@/lib/api';
import {
  requestNotificationPermission, getNotificationPermission, showNotification
} from '@/lib/notifications';

interface AlertsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  currentRate: number | null;
}

export default function AlertsPanel({ isOpen, onClose, currentRate }: AlertsPanelProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [templates, setTemplates] = useState<AlertTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [notificationPermission, setNotificationPermission] = useState<string>('default');

  // Form state
  const [formData, setFormData] = useState<AlertCreate>({
    name: '',
    alert_type: 'price_above',
    threshold_value: currentRate || 0.95,
    is_recurring: false,
    cooldown_minutes: 60,
    notify_push: true,
    notify_sound: true
  });

  useEffect(() => {
    if (isOpen) {
      loadAlerts();
      loadTemplates();
      setNotificationPermission(getNotificationPermission());
    }
  }, [isOpen]);

  useEffect(() => {
    if (currentRate) {
      setFormData(prev => ({
        ...prev,
        threshold_value: parseFloat(currentRate.toFixed(4))
      }));
    }
  }, [currentRate]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const data = await getAlerts(true);
      setAlerts(data);
    } catch (error) {
      console.error('Error loading alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const data = await getAlertTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createAlert(formData);
      setShowCreateForm(false);
      setFormData({
        name: '',
        alert_type: 'price_above',
        threshold_value: currentRate || 0.95,
        is_recurring: false,
        cooldown_minutes: 60,
        notify_push: true,
        notify_sound: true
      });
      await loadAlerts();
    } catch (error) {
      console.error('Error creating alert:', error);
    }
  };

  const handleDeleteAlert = async (id: number) => {
    if (!confirm('¿Eliminar esta alerta?')) return;
    try {
      await deleteAlert(id);
      await loadAlerts();
    } catch (error) {
      console.error('Error deleting alert:', error);
    }
  };

  const handleTogglePause = async (alert: Alert) => {
    try {
      if (alert.status === 'paused') {
        await resumeAlert(alert.id);
      } else {
        await pauseAlert(alert.id);
      }
      await loadAlerts();
    } catch (error) {
      console.error('Error toggling alert:', error);
    }
  };

  const handleEnableNotifications = async () => {
    const granted = await requestNotificationPermission();
    setNotificationPermission(granted ? 'granted' : 'denied');
    if (granted) {
      await showNotification('Notificaciones activadas', {
        body: 'Recibiras alertas de Forex Monitor'
      });
    }
  };

  const handleUseTemplate = (template: AlertTemplate) => {
    setFormData({
      name: template.name,
      alert_type: (template.config.alert_type as AlertType) || 'price_above',
      threshold_value: template.config.threshold_value || currentRate || 0.95,
      is_recurring: template.config.is_recurring || false,
      cooldown_minutes: template.config.cooldown_minutes || 60,
      notify_push: true,
      notify_sound: true
    });
    setShowCreateForm(true);
  };

  const handleCheckAlerts = async () => {
    try {
      const triggered = await checkAlerts();
      if (triggered.length > 0) {
        for (const t of triggered) {
          await showNotification(t.alert.name, { body: t.message });
        }
        await loadAlerts();
      } else {
        await showNotification('Alertas verificadas', { body: 'No hay alertas activadas' });
      }
    } catch (error) {
      console.error('Error checking alerts:', error);
    }
  };

  const getAlertTypeIcon = (type: string) => {
    switch (type) {
      case 'price_above': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'price_below': return <TrendingDown className="w-4 h-4 text-red-500" />;
      case 'percent_change': return <Percent className="w-4 h-4 text-blue-500" />;
      case 'sentiment': return <Activity className="w-4 h-4 text-purple-500" />;
      case 'news_impact': return <Newspaper className="w-4 h-4 text-orange-500" />;
      default: return <Bell className="w-4 h-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      active: 'bg-green-100 text-green-700',
      paused: 'bg-yellow-100 text-yellow-700',
      triggered: 'bg-blue-100 text-blue-700',
      expired: 'bg-gray-100 text-gray-500'
    };
    return (
      <span className={`text-xs px-2 py-0.5 rounded-full ${styles[status] || styles.active}`}>
        {status}
      </span>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold">Alertas</h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {/* Notification Permission */}
          {notificationPermission !== 'granted' && (
            <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-amber-800">
                    Activa las notificaciones para recibir alertas
                  </p>
                  <button
                    onClick={handleEnableNotifications}
                    className="mt-2 text-sm bg-amber-600 text-white px-3 py-1 rounded hover:bg-amber-700"
                  >
                    Activar notificaciones
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Create Form */}
          {showCreateForm ? (
            <form onSubmit={handleCreateAlert} className="space-y-4 mb-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-sm font-medium mb-1">Nombre</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Mi alerta"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Tipo de alerta</label>
                <select
                  value={formData.alert_type}
                  onChange={(e) => setFormData({ ...formData, alert_type: e.target.value as AlertType })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="price_above">Precio sube a...</option>
                  <option value="price_below">Precio baja a...</option>
                  <option value="percent_change">Cambio % en 24h</option>
                  <option value="sentiment">Cambio de sentimiento</option>
                  <option value="news_impact">Noticias de impacto</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Valor umbral {formData.alert_type === 'percent_change' ? '(%)' : ''}
                </label>
                <input
                  type="number"
                  step="0.0001"
                  value={formData.threshold_value}
                  onChange={(e) => setFormData({ ...formData, threshold_value: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_recurring}
                    onChange={(e) => setFormData({ ...formData, is_recurring: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm">Repetir alerta</span>
                </label>
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                >
                  Crear alerta
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-100"
                >
                  Cancelar
                </button>
              </div>
            </form>
          ) : (
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setShowCreateForm(true)}
                className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
              >
                <Plus className="w-4 h-4" />
                Nueva alerta
              </button>
              <button
                onClick={handleCheckAlerts}
                className="px-4 py-2 border rounded-lg hover:bg-gray-100"
                title="Verificar alertas ahora"
              >
                <Bell className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Templates */}
          {!showCreateForm && templates.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-2">Plantillas rapidas:</p>
              <div className="flex flex-wrap gap-2">
                {templates.slice(0, 3).map((t, i) => (
                  <button
                    key={i}
                    onClick={() => handleUseTemplate(t)}
                    className="text-xs px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
                  >
                    {t.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Alerts List */}
          {loading ? (
            <div className="text-center py-8 text-gray-500">Cargando alertas...</div>
          ) : alerts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Bell className="w-12 h-12 mx-auto mb-2 opacity-30" />
              <p>No tienes alertas configuradas</p>
            </div>
          ) : (
            <div className="space-y-2">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 border rounded-lg ${alert.status === 'paused' ? 'opacity-60' : ''}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-2">
                      {getAlertTypeIcon(alert.alert_type)}
                      <div>
                        <p className="font-medium text-sm">{alert.name}</p>
                        <p className="text-xs text-gray-500">
                          {alert.alert_type === 'percent_change'
                            ? `>${alert.threshold_value}%`
                            : alert.threshold_value.toFixed(4)}
                          {alert.is_recurring && ' (repetir)'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      {getStatusBadge(alert.status)}
                      <button
                        onClick={() => handleTogglePause(alert)}
                        className="p-1 hover:bg-gray-100 rounded"
                        title={alert.status === 'paused' ? 'Reanudar' : 'Pausar'}
                      >
                        {alert.status === 'paused' ? (
                          <Play className="w-4 h-4 text-green-600" />
                        ) : (
                          <Pause className="w-4 h-4 text-yellow-600" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDeleteAlert(alert.id)}
                        className="p-1 hover:bg-gray-100 rounded"
                        title="Eliminar"
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t bg-gray-50 text-center">
          <p className="text-xs text-gray-500">
            Las alertas se verifican automaticamente cada 5 minutos
          </p>
        </div>
      </div>
    </div>
  );
}
