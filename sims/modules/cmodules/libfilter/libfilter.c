#include "libfilter.h"
#include <stdio.h>
#include <stdlib.h>
int check_criterion(long criterion_type, double criterion_value, double toCheck){
	switch (criterion_type)
	{
	case GREATER_THAN:
		return toCheck > criterion_value;
	case GREATER_EQUAL:
		return toCheck >= criterion_value;
	case SMALLER_THAN:
		return toCheck < criterion_value;
	case SMALLER_EQUAL:
		return toCheck <= criterion_value;
	case EQUAL:
		return toCheck == criterion_value;
		
	}
}
void get_filtered_data(double* data_to_sort, int row_count, int col_count, long int* criterions_types, double* criterions_values, long* criterions_position, int criterion_count, double** sorted_data, int* sorted_count)
{
	size_t output_count = 0;
	double* data_to_output = NULL;
	for (int i = 0; i < row_count; i++)
	{
		//first, preallocate data that will be needed to return
		int all_criterions_correct = 1;
		for (int j = 0; j < criterion_count; j++){
			all_criterions_correct = all_criterions_correct && check_criterion(criterions_types[j], criterions_values[j], data_to_sort[i * col_count + criterions_position[j]]);
		}
		output_count += all_criterions_correct;
	}
	data_to_output = malloc(output_count * sizeof(double) * col_count);
	int current_output_id = 0;
	for (int i = 0; i < row_count; i++)
	{
		//first, preallocate data that will be needed to return
		int all_criterions_correct = 1;
		for (int j = 0; j < criterion_count; j++){
			all_criterions_correct = all_criterions_correct && check_criterion(criterions_types[j], criterions_values[j], data_to_sort[i * col_count + criterions_position[j]]);
		}
		if (all_criterions_correct){
			for (int j = 0; j < col_count; j++)
			{
				data_to_output[current_output_id * col_count + j] = data_to_sort[i * col_count + j];
			}
			current_output_id ++;
		}
	}
	*sorted_data = data_to_output;
	*sorted_count = output_count;
}
void freeArray(void* tofree){
	free(tofree);
}