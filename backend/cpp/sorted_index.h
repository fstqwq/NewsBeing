#include <vector>
#include <algorithm>
using std::vector, std::min;

vector <int> merge_sorted_list_or(vector<int> &a, vector<int> &b) {
    int i = 0, j = 0;
    vector<int> ret;
    while (i < a.size() && j < b.size()) {
        if (a[i] < b[j]) {
            ret.push_back(a[i]);
            i++;
        } else if (a[i] > b[j]) {
            ret.push_back(b[j]);
            j++;
        } else {
            ret.push_back(b[j]);
            i++;
            j++;
        }
    }
    while (i < a.size()) {
        ret.push_back(a[i]);
        i++;
    }
    while (j < b.size()) {
        ret.push_back(b[j]);
        j++;
    }
    return ret;
}

void merge_sorted_list_and_not_inplace(vector<int> &a, vector<int> &b) {
    int i = 0, j = 0, k = 0;
    while (i < a.size() && j < b.size()) {
        if (a[i] < b[j]) {
            a[k] = a[i];
            i++;
            k++;
        } else if (a[i] > b[j]) {
            j++;
        } else {
            i++;
            j++;
        }
    }
    while (i < a.size()) {
        a[k] = a[i];
        i++;
        k++;
    }
    a.erase(a.begin() + k, a.end());
}

void merge_sorted_list_and_inplace(vector<int> &a, vector<int> &b) {
    int i = 0, j = 0, k = 0;
    while (i < a.size() && j < b.size()) {
        if (a[i] < b[j]) {
            i++;
        } else if (a[i] > b[j]) {
            j++;
        } else {
            a[k] = a[i];
            i++;
            j++;
            k++;
        }
    }
    a.erase(a.begin() + k, a.end());
}

struct SortedIndex {

    vector<int> array;
    int total;
    bool comp;
    SortedIndex() = delete;
    SortedIndex(vector<int>&& _arr, int _tot, bool _comp = false) {
        array = _arr;
        total = _tot;
        comp = _comp;
    }
    SortedIndex(SortedIndex&& other) {
        array = std::move(other.array);
        total = std::move(other.total);
        comp = std::move(other.comp);
    }

    SortedIndex &operator|=(SortedIndex& other) {
        if (comp) {
            if (other.comp) {
                // NOT A OR NOT B -> NOT (A AND B)
                merge_sorted_list_and_inplace(array, other.array);
            } else {
                // NOT A OR B -> B - A
                merge_sorted_list_and_not_inplace(other.array, array);
                array = std::move(other.array);
                comp = false;
            }
        } else {
            if (other.comp) {
                // A OR NOT B -> NOT (B - A)
                merge_sorted_list_and_not_inplace(other.array, array);
                comp = true;
            } else {
                // A OR B
                array = merge_sorted_list_or(array, other.array);
            }
        }
        
        return *this;
    }

    SortedIndex &operator &=(SortedIndex& other) {
        if (comp) {
            if (other.comp) {
                // NOT A AND NOT B -> NOT (A OR B)
                array = merge_sorted_list_or(array, other.array);
                comp = false;
            } else {
                // NOT A AND B -> B - A
                merge_sorted_list_and_not_inplace(other.array, array);
                array = std::move(other.array);
            }
        } else {
            if (other.comp) {
                // A AND NOT B -> A - B
                merge_sorted_list_and_not_inplace(array, other.array);
            } else {
                // A AND B
                merge_sorted_list_and_inplace(array, other.array);
            }
        }
        return *this;
    }

    void negation() {
        comp = !comp;
    }

    size_t size() {
        return array.size();
    }

    vector <int> extractall() {
        return extract(size());
    }

    vector <int> extract(int max_count) {
        if (comp) {
            int j = 0;
            vector<int> ret;
            for (int i = 0; i < total; i++) {
                if (j < array.size() && i == array[j]) {
                    j++;
                } else {
                    ret.push_back(i);
                    if (ret.size() == max_count) {
                        break;
                    }
                }
            }
            return ret;
        } else {
            vector<int> ret;
            for (int i = 0; i < min((int) array.size(), max_count); i++) {
                ret.push_back(array[i]);
            }
            return ret;
        }
    }
    
};