from src import listing_metrics_config

def calc_score_segmented(number:float, lower:float, upper:float) -> int:
    if number < lower:
        score = 3
    elif number > upper:
        score = 1
    else:
        score = 2
    return(score)

def calc_cost_score(cost_dict:dict) -> int:
    monthly_cost = cost_dict['total']
    score = calc_score_segmented(
        number=monthly_cost,
        lower=3500,
        upper=4200
    )
    return(score)

def calc_av_model_score(form:dict) -> int:
    score = 0
    for _, row in listing_metrics_config.iterrows():
        metric = row['col']
        if row['db.type'] == 'Integer':
            if form[metric] != '':
                score += int(form[metric]) * row['av_model_weight'] * row['inverse_scoring']
        elif row['db.type'] == 'Boolean' and metric in form.keys():
            score += 1 * row['av_model_weight'] * row['inverse_scoring']
    return(int(score))

def calc_av_total_possible_score() -> int:
    max_score = 0
    for _, row in listing_metrics_config.iterrows():
        if row['db.type'] == 'Integer':
            max_score += 3 * row['av_model_weight'] * row['inverse_scoring']
        elif row['db.type'] == 'Boolean':
            max_score += 1 * row['av_model_weight'] * row['inverse_scoring']
    return(int(max_score))
