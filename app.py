from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def form():
    num_offers = 0
    num_criteria = 0
    return render_template('form.html', num_offers=num_offers, num_criteria=num_criteria)

@app.route('/MCDA', methods=['POST'])
def MCDA():
    num_offers = int(request.form['num_offers'])
    num_criteria = int(request.form['num_criteria'])

    # Initialize the weights and scores matrices
    weights = []
    scores = []

    # Get the names and weights of the criteria from the user
    criteria_names = []
    for i in range(num_criteria):
        criterion_name = request.form[f"criteria_name_{i+1}"]
        weight = float(request.form[f"criteria_weight_{i+1}"])
        criteria_names.append(criterion_name)
        weights.append(weight)

    # Get the scores for each offer and criterion from the user
    offer_names = []
    for i in range(num_offers):
        offer_name = request.form[f"offer_name_{i+1}"]
        offer_names.append(offer_name)
        offer_scores = []
        for j in range(num_criteria):
            score = float(request.form[f"offer_name_{i+1}_criteria_name_{i+1}"])
            offer_scores.append(score)
        scores.append(offer_scores)

    # Calculate the weighted score for each offer
    weighted_scores = []
    for i in range(num_offers):
        weighted_score = 0
        for j in range(num_criteria):
            weighted_score += weights[j] * scores[i][j]
        weighted_scores.append(weighted_score)

    # Find the index of the best offer
    best_offer_index = weighted_scores.index(max(weighted_scores))
    best_offer=offer_names[best_offer_index]
    
    # Return the best offer
    return render_template('MCDA.html', best_offer=best_offer)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Get the user input from the form
    num_options = int(request.form['num_options'])
    options = []
    costs = []
    probs = []
    
    for i in range(num_options):
        option_name = request.form[f"option_{i}_name"]
        cost = float(request.form[f"option_{i}_cost"])
        prob = float(request.form[f"option_{i}_prob"])
        options.append(option_name)
        costs.append(cost)
        probs.append(prob)

    # calculate Gittins indices
    gittins_indices = []
    for i in range(num_options):
        discount_factor = 2 * probs[i] * (1 - probs[i]) / sum(costs)
        gittins_index = probs[i] / (costs[i] / sum(costs) + discount_factor)
        gittins_indices.append(gittins_index)

    # calculate average high cost and average gittins indices
    sorted_numbers_ = sorted(costs)
    last_third = sorted_numbers_[-len(sorted_numbers_)//3:]
    avg_high_cost = sum(last_third) / len(last_third) # avg_prob = sum(probs) / len(probs)

    sorted_numbers = sorted(gittins_indices)
    last = sorted_numbers[-len(sorted_numbers)//24:]
    average_gittins_indices = sum(last) / len(last)

    # find the best option
    acceptable_options = []

    for i in range(num_options):
        if probs[i] > min(probs) and int(costs[i]) < int(avg_high_cost) and gittins_indices[i] <= average_gittins_indices:
            acceptable_options.append(i)

    gittins_acceptable_options = [gittins_indices[i] for i in acceptable_options]
    closest = None

    if len(gittins_acceptable_options) > 0:
        closest = min(gittins_acceptable_options, key=lambda x: abs(x - average_gittins_indices))

    if closest in gittins_acceptable_options:
        best_index = gittins_indices.index(closest)
        best_option = options[best_index]
        best_cost = costs[best_index]

        acceptable_options.remove(gittins_indices.index(closest))
        other_options = []
        for i in acceptable_options:
            if i != best_index:
                other_options.append((options[i], int(costs[i])))
        return render_template('gittins.html', best_option=best_option, best_cost=int(best_cost), other_options=other_options)
    return redirect(url_for('form'))

if __name__ == '__main__':
    app.run(debug=True)



