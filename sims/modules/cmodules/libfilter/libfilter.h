#define GREATER_THAN 1
#define GREATER_EQUAL 2
#define SMALLER_THAN 3
#define SMALLER_EQUAL 4
#define EQUAL 5


void freeArray(void* tofree);

void get_filtered_data(double* data_to_sort, int row_count, int col_count, long int* criterions_types, double* criterions_values, long* criterions_position, int criterion_count, double** sorted_data, int* sorted_count);

int check_criterion(long criterion_type, double criterion_value, double toCheck);