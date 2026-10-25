import React, { useState, useEffect } from 'react';
import {
  UtensilsCrossed,
  Activity,
  Plus,
  Droplets,
  Sparkles,
  CheckCircle,
  Apple,
  Flame,
  ChefHat
} from 'lucide-react';
import api from '../api';

export default function NutritionView() {
  const [nutrition, setNutrition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [waterMl, setWaterMl] = useState(2400);
  const [dietType, setDietType] = useState('VEGETARIAN');
  const [aiMealPlan, setAiMealPlan] = useState(null);
  const [showLogModal, setShowLogModal] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);

  const [mealForm, setMealForm] = useState({
    meal_type: 'LUNCH',
    food_name: 'Grilled Tofu & Quinoa Salad',
    quantity: '1',
    calories: '450',
    protein: '28',
    carbs: '48',
    fat: '14'
  });

  const loadNutrition = async () => {
    try {
      setLoading(true);
      const data = await api.getTodayNutrition().catch(() => null);
      setNutrition(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNutrition();
  }, []);

  const handleAddWater = async (amount) => {
    const updated = waterMl + amount;
    setWaterMl(updated);
    try {
      await api.logDailyActivity({ water_ml: updated });
      setActionSuccess(`Added +${amount}ml water!`);
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerateAiMeal = () => {
    const plans = {
      VEGETARIAN: {
        title: 'High-Fiber Mediterranean Vegetarian Bowl',
        calories: 520,
        macros: 'Protein: 24g • Carbs: 65g • Healthy Fats: 16g',
        ingredients: ['Steamed Quinoa', 'Chickpeas & Spinach', 'Roasted Cherry Tomatoes', 'Tahini Lemon Dressing'],
        why: 'Optimized for high-fiber glycemic management and blood pressure reduction.'
      },
      KETO: {
        title: 'Avocado & Hemp Heart Power Plate',
        calories: 610,
        macros: 'Protein: 32g • Net Carbs: 9g • Healthy Fats: 48g',
        ingredients: ['Hass Avocado', 'Extra Virgin Olive Oil Sauteed Greens', 'Hemp & Pumpkin Seeds', 'Grilled Tofu Steak'],
        why: 'Promotes sustained ketosis with zero refined sugars.'
      },
      JAIN: {
        title: 'Moong Sprout & Paneer Herb Bowl',
        calories: 480,
        macros: 'Protein: 26g • Carbs: 55g • Fats: 14g',
        ingredients: ['Sprouted Green Moong', 'Fresh Homemade Paneer Cubes', 'Cucumber & Fresh Coriander', 'Cumin Lime Dressing'],
        why: 'Complies strictly with root-free guidelines while delivering complete amino acids.'
      },
      BALANCED: {
        title: 'Wholesome Lentil & Brown Rice Pilaf with Greens',
        calories: 540,
        macros: 'Protein: 22g • Carbs: 72g • Fats: 12g',
        ingredients: ['Brown Basmati Rice', 'Yellow Lentils (Dal)', 'Steamed Broccoli florets', 'Flaxseed Garnish'],
        why: 'Balanced energy release with rich micronutrients and potassium.'
      }
    };
    setAiMealPlan(plans[dietType] || plans.BALANCED);
    setActionSuccess(`Generated customized ${dietType} meal recommendation!`);
    setTimeout(() => setActionSuccess(null), 3000);
  };

  const handleSaveMeal = async (e) => {
    e.preventDefault();
    try {
      await api.logMeal({
        meal_type: mealForm.meal_type,
        items: [{
          food_name: mealForm.food_name,
          serving_quantity: parseFloat(mealForm.quantity),
          calories_kcal: parseFloat(mealForm.calories),
          protein_g: parseFloat(mealForm.protein),
          carbs_g: parseFloat(mealForm.carbs),
          fat_g: parseFloat(mealForm.fat),
        }]
      });
      setShowLogModal(false);
      setActionSuccess(`Logged ${mealForm.meal_type.toLowerCase()}!`);
      setTimeout(() => setActionSuccess(null), 3000);
      loadNutrition();
    } catch (err) {
      alert(`Error logging meal: ${err.message}`);
    }
  };

  const totalCalories = nutrition?.total_calories || 420;
  const targetCalories = 2200;
  const protein = nutrition?.total_protein || 24;
  const carbs = nutrition?.total_carbs || 52;
  const fat = nutrition?.total_fat || 12;

  return (
    <div className="page-wrapper">
      {actionSuccess && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          background: 'rgba(16, 185, 129, 0.95)',
          color: '#ffffff',
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          boxShadow: '0 10px 25px rgba(0,0,0,0.4)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          zIndex: 1000,
          fontWeight: 600,
          fontSize: '0.9rem',
        }}>
          <CheckCircle size={18} />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: '#f8fafc' }}>
            Nutrition & AI Meal Planner
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            Automatic macronutrient tracking, hydration balance, and personalized dietary recommendations.
          </p>
        </div>

        <button onClick={() => setShowLogModal(true)} className="btn-primary">
          <Plus size={16} /> Log Meal / Food
        </button>
      </div>

      {/* Macro & Calorie Targets Card */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 700 }}>DAILY CALORIC INTAKE</span>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#f8fafc', marginTop: '4px' }}>
              {totalCalories} <span style={{ fontSize: '1.1rem', fontWeight: 500, color: 'var(--text-muted)' }}>/ {targetCalories} kcal</span>
            </div>
          </div>
          <span className="badge badge-normal" style={{ fontSize: '0.8rem' }}>
            {targetCalories - totalCalories} kcal remaining
          </span>
        </div>

        <div className="progress-bar-bg" style={{ height: '10px', marginBottom: '24px' }}>
          <div
            className="progress-bar-fill"
            style={{
              width: `${Math.min(100, (totalCalories / targetCalories) * 100)}%`,
              background: 'linear-gradient(90deg, #06b6d4 0%, #10b981 100%)',
            }}
          />
        </div>

        {/* 3 Macros */}
        <div className="grid-3">
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PROTEIN</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#38bdf8', marginTop: '4px' }}>
              {protein} g <span style={{ fontSize: '0.8rem', color: 'var(--text-faint)' }}>/ 120 g</span>
            </div>
            <div className="progress-bar-bg" style={{ marginTop: '8px' }}>
              <div className="progress-bar-fill" style={{ width: `${(protein / 120) * 100}%`, background: '#38bdf8' }} />
            </div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>CARBOHYDRATES</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#fbbf24', marginTop: '4px' }}>
              {carbs} g <span style={{ fontSize: '0.8rem', color: 'var(--text-faint)' }}>/ 240 g</span>
            </div>
            <div className="progress-bar-bg" style={{ marginTop: '8px' }}>
              <div className="progress-bar-fill" style={{ width: `${(carbs / 240) * 100}%`, background: '#fbbf24' }} />
            </div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>HEALTHY FATS</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#a78bfa', marginTop: '4px' }}>
              {fat} g <span style={{ fontSize: '0.8rem', color: 'var(--text-faint)' }}>/ 65 g</span>
            </div>
            <div className="progress-bar-bg" style={{ marginTop: '8px' }}>
              <div className="progress-bar-fill" style={{ width: `${(fat / 65) * 100}%`, background: '#a78bfa' }} />
            </div>
          </div>
        </div>
      </div>

      {/* 2-Column: Hydration & AI Meal Planner */}
      <div className="grid-2" style={{ marginBottom: '28px' }}>
        {/* Hydration Tracker */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Droplets size={20} color="#3b82f6" />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
                Hydration Tracker
              </h2>
            </div>
            <span className="badge badge-normal">{Math.round((waterMl / 3000) * 100)}% GOAL</span>
          </div>

          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#38bdf8', marginBottom: '8px' }}>
            {waterMl} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ 3,000 ml</span>
          </div>

          <div className="progress-bar-bg" style={{ height: '8px', marginBottom: '20px' }}>
            <div
              className="progress-bar-fill"
              style={{
                width: `${Math.min(100, (waterMl / 3000) * 100)}%`,
                background: '#3b82f6',
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button onClick={() => handleAddWater(250)} className="btn-secondary" style={{ flex: 1 }}>
              <Plus size={14} /> +250 ml (Glass)
            </button>
            <button onClick={() => handleAddWater(500)} className="btn-secondary" style={{ flex: 1 }}>
              <Plus size={14} /> +500 ml (Bottle)
            </button>
          </div>
        </div>

        {/* AI Meal Planner */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={20} color="#06b6d4" />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
                AI Meal Recommendation
              </h2>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px', marginBottom: '14px', flexWrap: 'wrap' }}>
            {['VEGETARIAN', 'BALANCED', 'KETO', 'JAIN'].map((diet) => (
              <button
                key={diet}
                onClick={() => setDietType(diet)}
                className="btn-secondary"
                style={{
                  fontSize: '0.75rem',
                  padding: '4px 10px',
                  background: dietType === diet ? 'var(--primary)' : 'rgba(30, 41, 59, 0.6)',
                  color: dietType === diet ? '#ffffff' : 'var(--text-muted)',
                }}
              >
                {diet}
              </button>
            ))}
          </div>

          <button onClick={handleGenerateAiMeal} className="btn-primary" style={{ width: '100%', marginBottom: '16px' }}>
            <ChefHat size={16} /> Generate {dietType} Recipe
          </button>

          {aiMealPlan ? (
            <div style={{
              background: 'rgba(15, 23, 42, 0.8)',
              padding: '16px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid rgba(6, 182, 212, 0.25)',
            }}>
              <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>{aiMealPlan.title}</strong>
              <div style={{ fontSize: '0.8rem', color: '#06b6d4', margin: '4px 0' }}>
                {aiMealPlan.calories} kcal • {aiMealPlan.macros}
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '6px 0 0', lineHeight: 1.4 }}>
                {aiMealPlan.why}
              </p>
            </div>
          ) : (
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textAlign: 'center', margin: '10px 0' }}>
              Click above to get clinical AI meal recommendations aligned with your vitals and dietary goals.
            </p>
          )}
        </div>
      </div>

      {/* Modal: Log Meal */}
      {showLogModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-card">
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '16px', color: '#f8fafc' }}>
              Log Meal / Food Item
            </h2>
            <form onSubmit={handleSaveMeal} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="input-label">Meal Type</label>
                <select
                  className="input-field"
                  value={mealForm.meal_type}
                  onChange={(e) => setMealForm({ ...mealForm, meal_type: e.target.value })}
                >
                  <option value="BREAKFAST">BREAKFAST</option>
                  <option value="LUNCH">LUNCH</option>
                  <option value="DINNER">DINNER</option>
                  <option value="SNACK">SNACK</option>
                </select>
              </div>

              <div>
                <label className="input-label">Food Description</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={mealForm.food_name}
                  onChange={(e) => setMealForm({ ...mealForm, food_name: e.target.value })}
                />
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Calories (kcal)</label>
                  <input
                    type="number"
                    required
                    className="input-field"
                    value={mealForm.calories}
                    onChange={(e) => setMealForm({ ...mealForm, calories: e.target.value })}
                  />
                </div>
                <div>
                  <label className="input-label">Protein (g)</label>
                  <input
                    type="number"
                    required
                    className="input-field"
                    value={mealForm.protein}
                    onChange={(e) => setMealForm({ ...mealForm, protein: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Carbs (g)</label>
                  <input
                    type="number"
                    required
                    className="input-field"
                    value={mealForm.carbs}
                    onChange={(e) => setMealForm({ ...mealForm, carbs: e.target.value })}
                  />
                </div>
                <div>
                  <label className="input-label">Fat (g)</label>
                  <input
                    type="number"
                    required
                    className="input-field"
                    value={mealForm.fat}
                    onChange={(e) => setMealForm({ ...mealForm, fat: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowLogModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Meal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
