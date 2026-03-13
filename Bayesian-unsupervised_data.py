# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 11:57:12 2026

@author: MACHCREATOR
""" 

import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# Configuration
N_SOLVERS = 2000
N_PUZZLES_PER_SOLVER = 50

# Strategy definitions (Sudoku techniques)
STRATEGIES = [
    'naked_single', 'hidden_single', 'naked_pair', 'hidden_pair',
    'naked_triple', 'pointing_pair', 'x_wing', 'swordfish',
    'xy_wing', 'forcing_chain', 'guess_backtrack', 'pattern_overlay'
]

# Archetype definitions with strategy probability profiles
ARCHETYPES = {
    'Systematic_Beginner': {
        'strategy_probs': [0.45, 0.40, 0.08, 0.04, 0.01, 0.015, 0.0, 0.0, 0.0, 0.0, 0.005, 0.0],
        'speed_factor': 2.5,
        'error_rate': 0.02,
        'hint_usage': 0.15,
        'persistence': 0.95,
        'verification_rate': 0.9
    },
    'Intuitive_Patterner': {
        'strategy_probs': [0.30, 0.20, 0.05, 0.05, 0.0, 0.10, 0.05, 0.0, 0.0, 0.0, 0.15, 0.10],
        'speed_factor': 1.2,
        'error_rate': 0.08,
        'hint_usage': 0.05,
        'persistence': 0.75,
        'verification_rate': 0.4
    },
    'Advanced_Logician': {
        'strategy_probs': [0.15, 0.15, 0.15, 0.15, 0.10, 0.10, 0.10, 0.05, 0.03, 0.015, 0.0, 0.005],
        'speed_factor': 1.8,
        'error_rate': 0.03,
        'hint_usage': 0.08,
        'persistence': 0.98,
        'verification_rate': 0.85
    },
    'Speed_Demon': {
        'strategy_probs': [0.50, 0.30, 0.05, 0.05, 0.0, 0.02, 0.0, 0.0, 0.0, 0.0, 0.08, 0.0],
        'speed_factor': 0.6,
        'error_rate': 0.12,
        'hint_usage': 0.02,
        'persistence': 0.60,
        'verification_rate': 0.2
    },
    'Backtrack_Gambler': {
        'strategy_probs': [0.25, 0.20, 0.05, 0.05, 0.0, 0.02, 0.0, 0.0, 0.0, 0.0, 0.40, 0.03],
        'speed_factor': 1.5,
        'error_rate': 0.18,
        'hint_usage': 0.10,
        'persistence': 0.70,
        'verification_rate': 0.3
    },
    'Adaptive_Master': {
        'strategy_probs': [0.10, 0.10, 0.12, 0.12, 0.10, 0.10, 0.12, 0.10, 0.08, 0.04, 0.01, 0.01],
        'speed_factor': 1.0,
        'error_rate': 0.01,
        'hint_usage': 0.03,
        'persistence': 0.99,
        'verification_rate': 0.75
    }
}

# Generate solver population
solver_data = []
solver_id = 0

for archetype_name, params in ARCHETYPES.items():
    # Uneven distribution
    if archetype_name == 'Systematic_Beginner':
        n_arch = 500
    elif archetype_name == 'Adaptive_Master':
        n_arch = 150
    elif archetype_name == 'Speed_Demon':
        n_arch = 400
    else:
        n_arch = (N_SOLVERS - 500 - 150 - 400) // 3
    
    for _ in range(n_arch):
        # Individual variation
        base_probs = np.array(params['strategy_probs'])
        noise = np.random.dirichlet(alpha=np.ones(len(STRATEGIES)) * 10)
        individual_probs = 0.85 * base_probs + 0.15 * noise
        individual_probs = individual_probs / individual_probs.sum()
        
        total_moves = np.random.poisson(450)
        strategy_counts = np.random.multinomial(total_moves, individual_probs)
        
        # Timing features
        avg_time_per_move = np.random.gamma(shape=2, scale=params['speed_factor'] * 5)
        pause_frequency = np.random.beta(2, 5) if params['speed_factor'] > 1 else np.random.beta(5, 2)
        thinking_time_variance = np.random.exponential(params['speed_factor'] * 10)
        
        # Error patterns
        total_errors = np.random.binomial(total_moves, params['error_rate'])
        correction_time = np.random.exponential(30) if total_errors > 0 else 0
        same_error_repeated = np.random.binomial(total_errors, 0.3) if total_errors > 0 else 0
        
        # Help-seeking
        hints_used = np.random.binomial(N_PUZZLES_PER_SOLVER, params['hint_usage'])
        
        # Behavioral
        give_up_rate = 1 - params['persistence'] + np.random.normal(0, 0.05)
        give_up_rate = np.clip(give_up_rate, 0, 1)
        verification_checks = np.random.poisson(params['verification_rate'] * 10)
        
        # Difficulty preference
        difficulty_pref = np.random.choice(['easy', 'medium', 'hard', 'expert'], 
                                         p=[0.1, 0.3, 0.4, 0.2] if 'Advanced' in archetype_name or 'Master' in archetype_name 
                                         else [0.4, 0.4, 0.15, 0.05])
        
        row = {
            'solver_id': solver_id,
            'true_archetype': archetype_name,
            **{f'strategy_{s}': count/total_moves for s, count in zip(STRATEGIES, strategy_counts)},
            **{f'count_{s}': count for s, count in zip(STRATEGIES, strategy_counts)},
            'avg_time_per_move': avg_time_per_move,
            'pause_frequency': pause_frequency,
            'thinking_time_variance': thinking_time_variance,
            'total_solving_time': avg_time_per_move * total_moves,
            'total_errors': total_errors,
            'error_rate': total_errors / total_moves if total_moves > 0 else 0,
            'correction_time': correction_time,
            'same_error_repeated': same_error_repeated,
            'error_recovery_efficiency': (total_errors - same_error_repeated) / total_errors if total_errors > 0 else 1.0,
            'hints_used_total': hints_used,
            'hint_dependency_ratio': hints_used / N_PUZZLES_PER_SOLVER,
            'hints_per_puzzle': hints_used / N_PUZZLES_PER_SOLVER,
            'give_up_rate': give_up_rate,
            'persistence_score': params['persistence'] + np.random.normal(0, 0.02),
            'verification_checks': verification_checks,
            'verification_rate': verification_checks / total_moves if total_moves > 0 else 0,
            'success_rate': np.random.beta(20 * params['persistence'], 5),
            'avg_puzzle_difficulty': {'easy': 1, 'medium': 2, 'hard': 3, 'expert': 4}[difficulty_pref],
            'strategy_diversity': len([c for c in strategy_counts if c > 0]) / len(STRATEGIES),
            'advanced_strategy_ratio': sum(strategy_counts[6:]) / total_moves if total_moves > 0 else 0,
            'basic_strategy_ratio': sum(strategy_counts[:2]) / total_moves if total_moves > 0 else 0,
            'total_puzzles_attempted': N_PUZZLES_PER_SOLVER,
            'total_moves': total_moves,
            'session_count': np.random.poisson(20) + 5
        }
        
        solver_data.append(row)
        solver_id += 1

# Create DataFrame
df = pd.DataFrame(solver_data)

# Add hybrid solvers (10% of data)
hybrid_indices = np.random.choice(df.index, size=int(0.1 * len(df)), replace=False)
for idx in hybrid_indices:
    current = df.loc[idx, 'true_archetype']
    other = np.random.choice([a for a in ARCHETYPES.keys() if a != current])
    
    for i, s in enumerate(STRATEGIES):
        curr_val = df.loc[idx, f'strategy_{s}']
        other_val = ARCHETYPES[other]['strategy_probs'][i]
        df.loc[idx, f'strategy_{s}'] = 0.6 * curr_val + 0.4 * other_val
    
    df.loc[idx, 'true_archetype'] = f'Hybrid_{current[:3]}_{other[:3]}'

# Save to CSV
import os

output_path = "C:/Users/MACHCREATOR/Downloads/alleadata2/sudoku_solver_strategies.csv"
os.makedirs("C:/Users/MACHCREATOR/Downloads/alleadata2", exist_ok=True)

df.to_csv(output_path, index=False)

#"C:\Users\MACHCREATOR\Downloads"